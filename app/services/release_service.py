import datetime
from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import (
    AppDeployGroup, ClusterInstance, CicdVariable,
    AppDeployGroupRelease, ClusterInstanceRelease, SysAuditLog
)
from app.utils.redis_lock import acquire_lock as redis_acquire_lock, release_lock as redis_release_lock


async def get_deploy_group(db: AsyncSession, env_code: str, app_code: str, group_code: str) -> AppDeployGroup | None:
    stmt = select(AppDeployGroup).where(
        and_(
            AppDeployGroup.env_code == env_code,
            AppDeployGroup.app_code == app_code,
            AppDeployGroup.group_code == group_code,
            AppDeployGroup.is_deleted == 0,
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_instances_by_group(db: AsyncSession, deploy_group_id: int) -> list[ClusterInstance]:
    """获取部署组下所有正常主机（过滤维护态）"""
    stmt = select(ClusterInstance).where(
        and_(
            ClusterInstance.deploy_group_id == deploy_group_id,
            ClusterInstance.instance_status == 1,  # 只返回正常主机
            ClusterInstance.is_deleted == 0,
        )
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_merged_variables(db: AsyncSession, env_code: str, app_code: str,
                                cluster_code: str = "", group_code: str = "") -> dict[str, str]:
    """多级变量合并：应用级 → 集群级 → 部署组级，按优先级覆盖"""
    stmt = select(CicdVariable).where(
        and_(
            CicdVariable.env_code == env_code,
            CicdVariable.app_code == app_code,
            CicdVariable.is_deleted == 0,
        )
    )
    result = await db.execute(stmt)
    all_vars = result.scalars().all()

    merged = {}
    for var in all_vars:
        # 按层级覆盖，同key高优先级覆盖低优先级
        if var.instance_id > 0:
            scope = 4
        elif var.group_code:
            scope = 3
        elif var.cluster_code:
            scope = 2
        else:
            scope = 1

        existing_scope = _var_scope(merged.get(f"__scope_{var.var_key}__", 0))
        if scope >= existing_scope:
            val = var.var_value
            merged[var.var_key] = val
            merged[f"__scope_{var.var_key}__"] = scope

    # 清理scope标记
    return {k: v for k, v in merged.items() if not k.startswith("__scope_")}


def _var_scope(scope: int) -> int:
    return scope if isinstance(scope, int) else 0


# ===== 发布前置 =====

async def release_before(db: AsyncSession, env_code: str, app_code: str,
                         group_code: str, trace_id: str, release_no: str,
                         timeout_minutes: int = 60) -> dict:
    """发布前置：幂等校验 + 锁抢占"""
    # 1. 幂等校验：查trace_id是否已处理
    stmt = select(SysAuditLog).where(
        and_(
            SysAuditLog.trace_id == trace_id,
            SysAuditLog.operation == "PUBLISH_BEFORE",
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        return {"success": True, "message": "幂等：已处理", "idempotent": True}

    # 2. 获取部署组
    group = await get_deploy_group(db, env_code, app_code, group_code)
    if not group:
        return {"success": False, "message": "部署组不存在"}

    # 3. 抢占DB发布锁（乐观锁风格）
    if group.lock_status == 1:
        return {"success": False, "message": f"部署组发布中，锁定trace_id={group.lock_trace_id}"}

    expire_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=timeout_minutes)
    stmt = (
        update(AppDeployGroup)
        .where(
            and_(
                AppDeployGroup.id == group.id,
                AppDeployGroup.lock_status == 0,  # 乐观锁条件
            )
        )
        .values(lock_status=1, lock_trace_id=trace_id, lock_expire_time=expire_time)
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        return {"success": False, "message": "锁抢占失败，并发冲突"}

    # 4. Redis分布式锁
    redis_ok = await redis_acquire_lock(env_code, app_code, group_code, trace_id, timeout_minutes * 60)
    if not redis_ok:
        # 回滚DB锁
        await db.execute(
            update(AppDeployGroup).where(AppDeployGroup.id == group.id).values(lock_status=0, lock_trace_id="", lock_expire_time=None)
        )
        return {"success": False, "message": "Redis锁抢占失败"}

    # 5. 记录审计
    audit = SysAuditLog(
        operator="jenkins-cd",
        operation="PUBLISH_BEFORE",
        target_table="app_deploy_group",
        target_biz_key=f"{env_code}/{app_code}/{group_code}",
        trace_id=trace_id,
        new_data={
            "release_no": release_no,
            "timeout_minutes": timeout_minutes,
            "lock_expire_time": expire_time.isoformat(),
        },
    )
    db.add(audit)

    return {"success": True, "message": "锁抢占成功", "lock_expire_time": expire_time.isoformat(), "idempotent": False}


# ===== 获取发布配置 =====

async def get_deploy_target(db: AsyncSession, env_code: str, app_code: str,
                            cluster_code: str, group_code: str) -> dict | None:
    """获取全量发布配置，过滤维护主机"""
    group = await get_deploy_group(db, env_code, app_code, group_code)
    if not group:
        return None

    instances = await get_instances_by_group(db, group.id)
    variables = await get_merged_variables(db, env_code, app_code, cluster_code, group_code)

    # 解密部署账号
    deploy_user = group.deploy_user or ""

    result = {
        "env_code": env_code,
        "app_code": app_code,
        "group_code": group_code,
        "group_type": group.group_type,
        "artifact_file_name": group.artifact_file_name,
        "deploy_path": group.deploy_path,
        "deploy_user": deploy_user,
        "deploy_strategy": group.deploy_strategy,
        "unpack_flag": group.unpack_flag,
        "jvm_opts": group.jvm_opts,
        "health_check_url": group.health_check_url,
        "start_script": group.start_script,
        "stop_script": group.stop_script,
        "variables": variables,
    }

    if group.group_type == "fixed":
        result["instances"] = [
            {
                "instance_id": inst.id,
                "instance_ip": inst.instance_ip,
                "ssh_port": inst.ssh_port,
                "instance_status": inst.instance_status,
                "bk_biz_id": inst.bk_biz_id,
                "bk_host_id": inst.bk_host_id,
                "bk_cloud_id": inst.bk_cloud_id,
                "bk_module_id": inst.bk_module_id,
                "bk_inner_ip": inst.bk_inner_ip,
                "instance_tags": inst.instance_tags,
                "deploy_user": inst.deploy_user,
                "deploy_path": inst.deploy_path,
                "health_check_url": inst.health_check_url,
                "start_script": inst.start_script,
                "stop_script": inst.stop_script,
            }
            for inst in instances
        ]
    else:
        result["tsf_config"] = {
            "deploy_group_id": group.deploy_group_id,
            "cpu_request": group.cpu_request,
            "cpu_limit": group.cpu_limit,
            "mem_request": group.mem_request,
            "mem_limit": group.mem_limit,
            "replicas": group.replicas,
            "tsf_traffic_weight": group.tsf_traffic_weight,
            "update_type": group.update_type,
        }

    return result


# ===== 发布后置 =====

async def release_after(db: AsyncSession, env_code: str, app_code: str,
                        cluster_id: int, group_code: str, trace_id: str,
                        build_no: str, artifact_version: str, release_user: str,
                        overall_status: str, instances: list[dict]) -> dict:
    """发布后置：版本回写 + 基线更新 + 锁释放"""
    # 1. 幂等校验
    stmt = select(SysAuditLog).where(
        and_(
            SysAuditLog.trace_id == trace_id,
            SysAuditLog.operation == "PUBLISH_AFTER",
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        return {"success": True, "message": "幂等：已处理", "idempotent": True}

    # 2. 获取部署组
    group = await get_deploy_group(db, env_code, app_code, group_code)
    if not group:
        return {"success": False, "message": "部署组不存在"}

    # 3. 写入基线版本（事务 + 乐观锁）
    if overall_status in ("success", "partial_success"):
        # 清空旧基线
        await db.execute(
            update(AppDeployGroupRelease).where(
                and_(
                    AppDeployGroupRelease.env_code == env_code,
                    AppDeployGroupRelease.app_code == app_code,
                    AppDeployGroupRelease.cluster_id == cluster_id,
                    AppDeployGroupRelease.group_code == group_code,
                )
            ).values(is_current=0)
        )
        # 写新基线
        baseline = AppDeployGroupRelease(
            env_code=env_code,
            app_code=app_code,
            cluster_id=cluster_id,
            group_code=group_code,
            build_no=build_no,
            artifact_version=artifact_version,
            release_user=release_user,
            release_status=overall_status,
            is_current=1,
            version=1,
        )
        db.add(baseline)
        await db.flush()
        baseline_id = baseline.id
    else:
        baseline_id = 0

    # 4. 批量写单机快照
    for inst in instances:
        snap = ClusterInstanceRelease(
            instance_id=inst["instance_id"],
            cluster_release_id=baseline_id,
            instance_ip=inst.get("instance_ip", ""),
            build_no=build_no,
            current_version=artifact_version,
            deploy_result=inst.get("deploy_result", "fail"),
        )
        db.add(snap)

    # 5. 释放DB锁
    await db.execute(
        update(AppDeployGroup).where(
            and_(
                AppDeployGroup.id == group.id,
                AppDeployGroup.lock_trace_id == trace_id,  # 校验锁归属
            )
        ).values(lock_status=0, lock_trace_id="", lock_expire_time=None)
    )

    # 6. 释放Redis锁
    await redis_release_lock(env_code, app_code, group_code, trace_id)

    # 7. 审计
    audit = SysAuditLog(
        operator=release_user,
        operation="PUBLISH_AFTER",
        target_table="app_deploy_group_release",
        target_biz_key=f"{env_code}/{app_code}/{group_code}",
        trace_id=trace_id,
        new_data={
            "build_no": build_no,
            "artifact_version": artifact_version,
            "overall_status": overall_status,
            "host_count": len(instances),
            "baseline_id": baseline_id,
        },
    )
    db.add(audit)

    return {"success": True, "message": "发布闭环完成", "baseline_id": baseline_id, "idempotent": False}
