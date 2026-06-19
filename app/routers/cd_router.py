from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import release_service

router = APIRouter(prefix="/api/v1/cd", tags=["Jenkins CD 流水线"])


class ReleaseBeforeRequest(BaseModel):
    release_trace_id: str = Field(..., description="全局发布追踪UUID")
    env_code: str = Field(..., description="环境编码")
    app_code: str = Field(..., description="应用编码")
    group_code: str = Field(default="default-group", description="分组编码")
    release_no: str = Field(..., description="Jenkins构建编号")
    timeout_minute: int = Field(default=60, description="锁超时分钟")


class GetDeployTargetRequest(BaseModel):
    env_code: str
    app_code: str
    cluster_code: str = ""
    group_code: str = "default-group"


class InstanceResult(BaseModel):
    instance_id: int
    instance_ip: str = ""
    deploy_result: str = "success"  # success/fail


class ReleaseAfterRequest(BaseModel):
    release_trace_id: str
    env_code: str
    app_code: str
    cluster_id: int
    group_code: str = "default-group"
    build_no: str
    artifact_version: str
    release_user: str = "jenkins-cd"
    overall_status: str = "success"  # success/partial_success/fail
    instances: list[InstanceResult] = []


@router.post("/release-before", summary="发布前置：告警管控+发布锁抢占")
async def release_before(req: ReleaseBeforeRequest, db: AsyncSession = Depends(get_db)):
    result = await release_service.release_before(
        db=db,
        env_code=req.env_code,
        app_code=req.app_code,
        group_code=req.group_code,
        trace_id=req.release_trace_id,
        release_no=req.release_no,
        timeout_minutes=req.timeout_minute,
    )
    if not result["success"]:
        raise HTTPException(status_code=409, detail=result["message"])
    return result


@router.post("/get-deploy-target", summary="获取全量发布配置")
async def get_deploy_target(req: GetDeployTargetRequest, db: AsyncSession = Depends(get_db)):
    result = await release_service.get_deploy_target(
        db=db,
        env_code=req.env_code,
        app_code=req.app_code,
        cluster_code=req.cluster_code,
        group_code=req.group_code,
    )
    if not result:
        raise HTTPException(status_code=404, detail="部署组不存在或未配置")
    return {"success": True, "data": result}


@router.post("/release-after", summary="发布后置：版本回写+告警恢复+锁释放")
async def release_after(req: ReleaseAfterRequest, db: AsyncSession = Depends(get_db)):
    result = await release_service.release_after(
        db=db,
        env_code=req.env_code,
        app_code=req.app_code,
        cluster_id=req.cluster_id,
        group_code=req.group_code,
        trace_id=req.release_trace_id,
        build_no=req.build_no,
        artifact_version=req.artifact_version,
        release_user=req.release_user,
        overall_status=req.overall_status,
        instances=[i.model_dump() for i in req.instances],
    )
    if not result["success"]:
        raise HTTPException(status_code=409, detail=result["message"])
    return result


@router.get("/release-status", summary="查询发布锁状态")
async def release_status(env_code: str, app_code: str, group_code: str = "default-group"):
    from app.utils.redis_lock import check_lock
    return await check_lock(env_code, app_code, group_code)
