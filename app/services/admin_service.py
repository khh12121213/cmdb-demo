from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import (
    EnvInfo, AppInfo, AppCluster, AppDeployGroup,
    ClusterInstance, CicdVariable,
    AppDeployGroupRelease, ClusterInstanceRelease, SysAuditLog
)
from app.utils.crypto import decrypt_value


# ===== 环境管理 =====
async def get_envs(db: AsyncSession, page: int = 1, size: int = 20, tags: str = "") -> dict:
    stmt = select(EnvInfo).where(EnvInfo.is_deleted == 0)
    if tags:
        stmt = stmt.where(EnvInfo.env_tags.contains(tags))
    # count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    # page
    stmt = stmt.offset((page - 1) * size).limit(size)
    rows = (await db.execute(stmt)).scalars().all()
    return {"total": total, "items": [r for r in rows]}


async def save_env(db: AsyncSession, data: dict) -> EnvInfo:
    if data.get("id"):
        env = (await db.execute(select(EnvInfo).where(EnvInfo.id == data["id"]))).scalar_one_or_none()
    else:
        env = EnvInfo()
        db.add(env)
    env.env_code = data["env_code"]
    env.env_name = data["env_name"]
    env.env_tags = data.get("env_tags", "")
    return env


# ===== 应用管理 =====
async def get_apps(db: AsyncSession, page: int = 1, size: int = 20, keyword: str = "") -> dict:
    stmt = select(AppInfo).where(AppInfo.is_deleted == 0)
    if keyword:
        stmt = stmt.where(AppInfo.app_code.contains(keyword) | AppInfo.app_name.contains(keyword))
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    stmt = stmt.offset((page - 1) * size).limit(size)
    rows = (await db.execute(stmt)).scalars().all()
    return {"total": total, "items": [r for r in rows]}


async def save_app(db: AsyncSession, data: dict) -> AppInfo:
    if data.get("id"):
        app = (await db.execute(select(AppInfo).where(AppInfo.id == data["id"]))).scalar_one_or_none()
    else:
        app = AppInfo()
        db.add(app)
    for f in ["app_code", "app_name", "app_type", "repo_url", "artifact_repo", "owner", "proc_name", "base_jvm_opts", "log_base_dir"]:
        if f in data:
            setattr(app, f, data[f])
    for f in ["server_port", "management_port", "default_bk_biz_id"]:
        if f in data and data[f] is not None:
            setattr(app, f, int(data[f]))
    return app


async def get_apps_all(db: AsyncSession) -> list:
    stmt = select(AppInfo).where(AppInfo.is_deleted == 0)
    return list((await db.execute(stmt)).scalars().all())


# ===== 集群管理 =====
async def get_clusters(db: AsyncSession, env_code: str = "", app_code: str = "", page: int = 1, size: int = 20) -> dict:
    stmt = select(AppCluster).where(AppCluster.is_deleted == 0)
    if env_code:
        stmt = stmt.where(AppCluster.env_code == env_code)
    if app_code:
        stmt = stmt.where(AppCluster.app_code == app_code)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    stmt = stmt.offset((page - 1) * size).limit(size)
    rows = (await db.execute(stmt)).scalars().all()
    return {"total": total, "items": [r for r in rows]}


async def save_cluster(db: AsyncSession, data: dict) -> AppCluster:
    if data.get("id"):
        cl = (await db.execute(select(AppCluster).where(AppCluster.id == data["id"]))).scalar_one_or_none()
    else:
        cl = AppCluster()
        db.add(cl)
    for f in ["env_code", "app_code", "cluster_code", "cluster_name", "deploy_mode", "tsf_cluster_id", "namespace", "labels"]:
        if f in data:
            setattr(cl, f, data[f])
    if "status" in data:
        cl.status = int(data["status"])
    return cl


# ===== 部署组管理 =====
async def get_deploy_groups(db: AsyncSession, env_code: str = "", app_code: str = "",
                             page: int = 1, size: int = 20) -> dict:
    stmt = select(AppDeployGroup).where(AppDeployGroup.is_deleted == 0)
    if env_code:
        stmt = stmt.where(AppDeployGroup.env_code == env_code)
    if app_code:
        stmt = stmt.where(AppDeployGroup.app_code == app_code)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    stmt = stmt.order_by(AppDeployGroup.id.desc()).offset((page - 1) * size).limit(size)
    rows = (await db.execute(stmt)).scalars().all()
    return {"total": total, "items": [r for r in rows]}


async def save_deploy_group(db: AsyncSession, data: dict) -> AppDeployGroup:
    if data.get("id"):
        g = (await db.execute(select(AppDeployGroup).where(AppDeployGroup.id == data["id"]))).scalar_one_or_none()
    else:
        g = AppDeployGroup()
        db.add(g)
    fields = ["env_code", "app_code", "cluster_id", "group_code", "group_name",
              "deploy_group_id", "group_type", "status",
              "artifact_file_name", "deploy_path", "deploy_strategy", "unpack_flag",
              "jvm_opts", "health_check_url", "start_script", "stop_script",
              "cpu_request", "cpu_limit", "mem_request", "mem_limit", "replicas",
              "tsf_traffic_weight", "middleware_domain", "middleware_cluster_name",
              "admin_url", "package_type"]
    for f in fields:
        if f in data:
            setattr(g, f, data[f])
    if data.get("deploy_user"):
        from app.utils.crypto import encrypt_value
        g.deploy_user = encrypt_value(data["deploy_user"])
    return g


# ===== 主机管理 =====
async def get_instances(db: AsyncSession, group_id: int = 0, page: int = 1, size: int = 50) -> dict:
    stmt = select(ClusterInstance).where(ClusterInstance.is_deleted == 0)
    if group_id:
        stmt = stmt.where(ClusterInstance.deploy_group_id == group_id)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    stmt = stmt.offset((page - 1) * size).limit(size)
    rows = (await db.execute(stmt)).scalars().all()
    return {"total": total, "items": [r for r in rows]}


async def save_instance(db: AsyncSession, data: dict) -> ClusterInstance:
    if data.get("id"):
        inst = (await db.execute(select(ClusterInstance).where(ClusterInstance.id == data["id"]))).scalar_one_or_none()
    else:
        inst = ClusterInstance()
        db.add(inst)
    fields = ["deploy_group_id", "instance_ip", "ssh_port",
              "bk_biz_id", "bk_host_id", "bk_cloud_id", "bk_module_id", "bk_inner_ip",
              "instance_tags", "instance_status", "deploy_path"]
    for f in fields:
        if f in data and data[f] is not None:
            setattr(inst, f, data[f])
    return inst


async def update_instance_status(db: AsyncSession, instance_id: int, status: int) -> bool:
    stmt = update(ClusterInstance).where(ClusterInstance.id == instance_id).values(instance_status=status)
    result = await db.execute(stmt)
    return result.rowcount > 0


async def bind_instance_group(db: AsyncSession, instance_ids: list[int], group_id: int) -> int:
    stmt = update(ClusterInstance).where(ClusterInstance.id.in_(instance_ids)).values(deploy_group_id=group_id)
    result = await db.execute(stmt)
    return result.rowcount


# ===== 变量管理 =====
async def get_variables(db: AsyncSession, env_code: str = "", app_code: str = "",
                        page: int = 1, size: int = 50, show_secret: bool = False) -> dict:
    stmt = select(CicdVariable).where(CicdVariable.is_deleted == 0)
    if env_code:
        stmt = stmt.where(CicdVariable.env_code == env_code)
    if app_code:
        stmt = stmt.where(CicdVariable.app_code == app_code)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    stmt = stmt.offset((page - 1) * size).limit(size)
    rows = (await db.execute(stmt)).scalars().all()
    items = []
    for r in rows:
        d = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        if not show_secret and r.is_secret == 1:
            d["var_value"] = "******"
            d["encrypt_value"] = "******"
        else:
            d["var_value"] = decrypt_value(r.encrypt_value) if r.is_secret else r.var_value
        items.append(d)
    return {"total": total, "items": items}


async def save_variable(db: AsyncSession, data: dict) -> CicdVariable:
    from app.utils.crypto import encrypt_value
    if data.get("id"):
        v = (await db.execute(select(CicdVariable).where(CicdVariable.id == data["id"]))).scalar_one_or_none()
    else:
        v = CicdVariable()
        db.add(v)
    for f in ["env_code", "app_code", "cluster_code", "group_code", "instance_id", "var_key", "remark"]:
        if f in data:
            setattr(v, f, data[f])
    is_secret = int(data.get("is_secret", 0))
    v.is_secret = is_secret
    if is_secret:
        v.encrypt_value = encrypt_value(data.get("var_value", ""))
        v.var_value = ""
    else:
        v.var_value = data.get("var_value", "")
        v.encrypt_value = None
    return v


# ===== 基线/快照/审计 (只读) =====
async def get_releases(db: AsyncSession, env_code: str = "", app_code: str = "",
                       page: int = 1, size: int = 20) -> dict:
    stmt = select(AppDeployGroupRelease).where(AppDeployGroupRelease.is_deleted == 0)
    if env_code:
        stmt = stmt.where(AppDeployGroupRelease.env_code == env_code)
    if app_code:
        stmt = stmt.where(AppDeployGroupRelease.app_code == app_code)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    stmt = stmt.order_by(AppDeployGroupRelease.id.desc()).offset((page - 1) * size).limit(size)
    rows = (await db.execute(stmt)).scalars().all()
    return {"total": total, "items": [r for r in rows]}


async def get_instance_releases(db: AsyncSession, instance_id: int = 0, page: int = 1, size: int = 20) -> dict:
    stmt = select(ClusterInstanceRelease).where(ClusterInstanceRelease.is_deleted == 0)
    if instance_id:
        stmt = stmt.where(ClusterInstanceRelease.instance_id == instance_id)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    stmt = stmt.order_by(ClusterInstanceRelease.id.desc()).offset((page - 1) * size).limit(size)
    rows = (await db.execute(stmt)).scalars().all()
    return {"total": total, "items": [r for r in rows]}


async def get_audit_logs(db: AsyncSession, page: int = 1, size: int = 20,
                         operator: str = "", operation: str = "") -> dict:
    stmt = select(SysAuditLog).order_by(SysAuditLog.id.desc())
    if operator:
        stmt = stmt.where(SysAuditLog.operator == operator)
    if operation:
        stmt = stmt.where(SysAuditLog.operation == operation)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar()
    stmt = stmt.offset((page - 1) * size).limit(size)
    rows = (await db.execute(stmt)).scalars().all()
    return {"total": total, "items": [r for r in rows]}


# ===== 逻辑删除通用 =====
async def soft_delete(db: AsyncSession, model_class, obj_id: int) -> bool:
    stmt = update(model_class).where(model_class.id == obj_id).values(is_deleted=1)
    result = await db.execute(stmt)
    return result.rowcount > 0
