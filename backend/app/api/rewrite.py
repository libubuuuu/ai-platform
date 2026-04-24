"""功能2：AI 洗稿 / 复刻。"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.integrations.ai import rewrite as rw
from app.models.content import CrawledContent, RewrittenContent
from app.models.user import User
from app.schemas.content import RewriteRequest, RewrittenContentOut

router = APIRouter(prefix="/api/rewrite", tags=["rewrite"])
settings = get_settings()


@router.post("", response_model=RewrittenContentOut)
async def rewrite(
    req: RewriteRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if not req.content_ids:
        raise HTTPException(400, "至少需要一条内容")

    # 取源内容
    result = await db.execute(
        select(CrawledContent).where(CrawledContent.id.in_(req.content_ids))
    )
    sources = list(result.scalars().all())
    if not sources:
        raise HTTPException(404, "内容不存在")

    sources_dict = [
        {
            "id": s.id,
            "title": s.title,
            "content_text": s.content_text,
            "images": s.images,
            "video_url": s.video_url,
        }
        for s in sources
    ]

    # 洗稿
    if req.mode == "merge":
        result_text = await rw.rewrite_merge(sources_dict, req.target_platform)
    else:
        result_text = await rw.rewrite_single(sources_dict[0], req.target_platform)

    # 媒体"复刻"：这里简单策略——直接复用源图片/视频
    # （AI 再生成图片走功能3，用户可在画布里进一步处理）
    merged_images = []
    merged_video = ""
    for s in sources:
        merged_images.extend(s.images or [])
        if not merged_video and s.video_url:
            merged_video = s.video_url

    # 取 user
    user_result = await db.execute(select(User).where(User.username == user["username"]))
    u = user_result.scalar_one()

    obj = RewrittenContent(
        user_id=u.id,
        source_content_ids=[s.id for s in sources],
        mode=req.mode,
        title=result_text["title"],
        content_text=result_text["content"],
        images=merged_images,
        video_url=merged_video,
        ai_provider=settings.DEFAULT_AI_PROVIDER,
        ai_model=(
            settings.ANTHROPIC_MODEL
            if settings.DEFAULT_AI_PROVIDER == "anthropic"
            else settings.OPENAI_MODEL
        ),
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("/list", response_model=List[RewrittenContentOut])
async def list_rewrites(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
    limit: int = 50,
):
    user_result = await db.execute(select(User).where(User.username == user["username"]))
    u = user_result.scalar_one()
    result = await db.execute(
        select(RewrittenContent)
        .where(RewrittenContent.user_id == u.id)
        .order_by(RewrittenContent.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
