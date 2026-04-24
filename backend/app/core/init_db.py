"""数据库初始化：建表 + 创建 admin 账户。

使用方法：
    python -m app.core.init_db
"""
import asyncio

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import Base, AsyncSessionLocal, engine
from app.core.security import hash_password
from app.models.user import User
# 导入所有模型以让 SQLAlchemy 识别它们
from app.models import user, platform_account, content, cart, task  # noqa


async def init_db() -> None:
    settings = get_settings()

    # 1. 建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. 创建 admin 账户（如不存在）
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == settings.ADMIN_USERNAME)
        )
        existing = result.scalar_one_or_none()

        if existing is None:
            admin = User(
                username=settings.ADMIN_USERNAME,
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                is_admin=True,
            )
            session.add(admin)
            await session.commit()
            print(f"✅ Admin 账户已创建：{settings.ADMIN_USERNAME}")
        else:
            print(f"ℹ️  Admin 账户已存在：{settings.ADMIN_USERNAME}")

    print("✅ 数据库初始化完成")


if __name__ == "__main__":
    asyncio.run(init_db())
