from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import admin_service as svc
from app.models import EnvInfo, SysInfo, AppInfo, AppCluster, AppDeployGroup, ClusterInstance, CicdVariable

router = APIRouter(prefix="/api/v1/admin", tags=["运维管理"])

# ===== 环境管理 =====
@router.get("/env/list")
async def env_list(page: int = 1, size: int = 20, tags: str = "", db: AsyncSession = Depends(get_db)):
    return await svc.get_envs(db, page, size, tags)

@router.post("/env/save")
async def env_save(data: dict, db: AsyncSession = Depends(get_db)):
    await svc.save_env(db, data)
    return {"success": True}

@router.put("/env/remove")
async def env_remove(id: int, db: AsyncSession = Depends(get_db)):
    ok = await svc.soft_delete(db, EnvInfo, id)
    return {"success": ok}

# ===== 系统管理 =====
@router.get("/sys/list")
async def sys_list(page: int = 1, size: int = 20, db: AsyncSession = Depends(get_db)):
    return await svc.get_sys_list(db, page, size)

@router.post("/sys/save")
async def sys_save(data: dict, db: AsyncSession = Depends(get_db)):
    await svc.save_sys(db, data)
    return {"success": True}

@router.put("/sys/remove")
async def sys_remove(id: int, db: AsyncSession = Depends(get_db)):
    ok = await svc.soft_delete(db, SysInfo, id)
    return {"success": ok}

# ===== 应用管理 =====
@router.get("/app/list")
async def app_list(page: int = 1, size: int = 20, keyword: str = "", db: AsyncSession = Depends(get_db)):
    return await svc.get_apps(db, page, size, keyword)

@router.get("/app/all")
async def app_all(db: AsyncSession = Depends(get_db)):
    return await svc.get_apps_all(db)

@router.post("/app/save")
async def app_save(data: dict, db: AsyncSession = Depends(get_db)):
    await svc.save_app(db, data)
    return {"success": True}

@router.get("/app/detail")
async def app_detail(id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    r = (await db.execute(select(AppInfo).where(AppInfo.id == id))).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "不存在")
    return {c.name: getattr(r, c.name) for c in r.__table__.columns}

@router.put("/app/remove")
async def app_remove(id: int, db: AsyncSession = Depends(get_db)):
    ok = await svc.soft_delete(db, AppInfo, id)
    return {"success": ok}

# ===== 集群管理 =====
@router.get("/cluster/list")
async def cluster_list(env_code: str = "", app_code: str = "", page: int = 1, size: int = 20,
                       db: AsyncSession = Depends(get_db)):
    return await svc.get_clusters(db, env_code, app_code, page, size)

@router.post("/cluster/save")
async def cluster_save(data: dict, db: AsyncSession = Depends(get_db)):
    await svc.save_cluster(db, data)
    return {"success": True}

@router.put("/cluster/status")
async def cluster_status(id: int, status: int = 1, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import update
    await db.execute(update(AppCluster).where(AppCluster.id == id).values(status=status))
    return {"success": True}

@router.put("/cluster/remove")
async def cluster_remove(id: int, db: AsyncSession = Depends(get_db)):
    ok = await svc.soft_delete(db, AppCluster, id)
    return {"success": ok}

# ===== 部署组管理 =====
@router.get("/group/list")
async def group_list(env_code: str = "", app_code: str = "", page: int = 1, size: int = 20,
                     db: AsyncSession = Depends(get_db)):
    return await svc.get_deploy_groups(db, env_code, app_code, page, size)

@router.post("/group/save")
async def group_save(data: dict, db: AsyncSession = Depends(get_db)):
    await svc.save_deploy_group(db, data)
    return {"success": True}

@router.put("/group/remove")
async def group_remove(id: int, db: AsyncSession = Depends(get_db)):
    ok = await svc.soft_delete(db, AppDeployGroup, id)
    return {"success": ok}

# ===== 主机实例管理 =====
@router.get("/instance/list")
async def instance_list(group_id: int = 0, page: int = 1, size: int = 50, db: AsyncSession = Depends(get_db)):
    return await svc.get_instances(db, group_id, page, size)

@router.post("/instance/save")
async def instance_save(data: dict, db: AsyncSession = Depends(get_db)):
    await svc.save_instance(db, data)
    return {"success": True}

@router.put("/instance/status")
async def instance_status(id: int, status: int, db: AsyncSession = Depends(get_db)):
    ok = await svc.update_instance_status(db, id, status)
    return {"success": ok}

@router.put("/instance/bind-group")
async def instance_bind_group(ids: list[int], group_id: int, db: AsyncSession = Depends(get_db)):
    count = await svc.bind_instance_group(db, ids, group_id)
    return {"success": True, "count": count}

# ===== 变量管理 =====
@router.get("/variable/list")
async def variable_list(env_code: str = "", app_code: str = "", page: int = 1, size: int = 50,
                        db: AsyncSession = Depends(get_db)):
    return await svc.get_variables(db, env_code, app_code, page, size)

@router.post("/variable/save")
async def variable_save(data: dict, db: AsyncSession = Depends(get_db)):
    await svc.save_variable(db, data)
    return {"success": True}

@router.delete("/variable/remove")
async def variable_remove(id: int, db: AsyncSession = Depends(get_db)):
    ok = await svc.soft_delete(db, CicdVariable, id)
    return {"success": ok}

# ===== 发布基线 / 单机快照 / 审计 (只读) =====
@router.get("/release/baseline")
async def release_baseline(env_code: str = "", app_code: str = "", page: int = 1, size: int = 20,
                           db: AsyncSession = Depends(get_db)):
    return await svc.get_releases(db, env_code, app_code, page, size)

@router.get("/release/instance-snaps")
async def instance_snaps(instance_id: int = 0, page: int = 1, size: int = 20,
                         db: AsyncSession = Depends(get_db)):
    return await svc.get_instance_releases(db, instance_id, page, size)

@router.get("/audit/list")
async def audit_list(page: int = 1, size: int = 20, operator: str = "", operation: str = "",
                     db: AsyncSession = Depends(get_db)):
    return await svc.get_audit_logs(db, page, size, operator, operation)

# ===== 枚举 =====
@router.get("/enums")
async def enums():
    return {
        "app_types": ["springboot", "nginx", "tongweb", "weblogic", "tsf-service"],
        "deploy_modes": ["fixed", "elastic"],
        "deploy_strategys": ["full", "incr"],
        "package_types": ["jar", "war", "tar"],
        "env_codes": ["dev", "test", "staging", "prod"],
    }
