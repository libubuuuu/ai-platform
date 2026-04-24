"""功能2的前半部分：购物车。"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.cart import CartItem
from app.models.content import CrawledContent
from app.models.user import User
from app.schemas.content import CartAddRequest, CartOut, ContentOut

router = APIRouter(prefix="/api/cart", tags=["cart"])


async def _resolve_user(db: AsyncSession, username: str) -> User:
    result = await db.execute(select(User).where(User.username == username))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "用户不存在")
    return u


@router.post("/add")
async def add_to_cart(
    req: CartAddRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    u = await _resolve_user(db, user["username"])

    # 防重复
    exist = await db.execute(
        select(CartItem).where(
            CartItem.user_id == u.id,
            CartItem.content_id == req.content_id,
        )
    )
    if exist.scalar_one_or_none():
        return {"ok": True, "msg": "已在购物车中"}

    item = CartItem(user_id=u.id, content_id=req.content_id)
    db.add(item)
    await db.commit()
    return {"ok": True, "msg": "已加入购物车"}


@router.get("", response_model=CartOut)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    u = await _resolve_user(db, user["username"])
    # 联表查内容
    result = await db.execute(
        select(CrawledContent)
        .join(CartItem, CartItem.content_id == CrawledContent.id)
        .where(CartItem.user_id == u.id)
        .order_by(CartItem.added_at.desc())
    )
    items = list(result.scalars().all())
    return CartOut(count=len(items), items=[ContentOut.model_validate(i) for i in items])


@router.delete("/{content_id}")
async def remove_from_cart(
    content_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    u = await _resolve_user(db, user["username"])
    await db.execute(
        delete(CartItem).where(
            CartItem.user_id == u.id,
            CartItem.content_id == content_id,
        )
    )
    await db.commit()
    return {"ok": True}


@router.delete("")
async def clear_cart(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    u = await _resolve_user(db, user["username"])
    await db.execute(delete(CartItem).where(CartItem.user_id == u.id))
    await db.commit()
    return {"ok": True}
