"""鉴权路由：登录、我的信息。

为简化骨架，暂时只支持 admin 单用户登录（对应你需求里"只有我能用"）。
后续要扩展普通用户，只需在 User 表里注册新记录并打开 /api/auth/register。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_user,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserMe

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token = create_access_token({
        "sub": user.username,
        "is_admin": user.is_admin,
    })
    return TokenResponse(
        access_token=token,
        is_admin=user.is_admin,
        username=user.username,
    )


@router.get("/me", response_model=UserMe)
async def me(user: dict = Depends(get_current_user)):
    return UserMe(username=user["username"], is_admin=user["is_admin"])
