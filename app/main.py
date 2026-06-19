import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
