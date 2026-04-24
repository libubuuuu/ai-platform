"""FastAPI 应用入口。

启动：
    uvicorn app.main:app --reload --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api import auth, cart, comment, content, image, publish, rewrite
from app.core.config import get_settings
from app.core.database import Base, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 {settings.APP_NAME} 启动中...")
    # 自动建表（生产环境建议改用 alembic）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ 数据库就绪")
    yield
    logger.info("👋 应用关闭")


app = FastAPI(
    title=settings.APP_NAME,
    description="多平台内容智能运营系统 · 双引擎：MediaCrawler + social-auto-upload",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(cart.router)
app.include_router(rewrite.router)
app.include_router(image.router)
app.include_router(publish.router)
app.include_router(comment.router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}
