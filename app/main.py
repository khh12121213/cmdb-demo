import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.database import engine, Base
from app.routers import cd_router, admin_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时自动建表
    async with engine.begin() as conn:
        from app import models  # noqa: ensure all models loaded
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="银行CI/CD-CMDB Demo",
    description="纯配置型CMDB + 发布锁 + 基线管理 + 审计 — Demo验证版",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cd_router.router)
app.include_router(admin_router.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/ready")
async def ready():
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "fail", "db": str(e)}


# 生产模式托管前端静态文件
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str = ""):
        """SPA fallback：所有非 /api 路径返回 index.html"""
        file_path = os.path.join(frontend_dist, full_path) if full_path else ""
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
