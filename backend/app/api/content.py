"""功能1：多平台内容发现与监测。

- POST /api/content/search - 按关键词搜索
- POST /api/content/trending - 获取平台热门
- GET  /api/content/list - 列表已抓取的内容（支持平台/tag过滤）
- GET  /api/content/{id} - 详情
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.integrations.ai.rewrite import analyze_keyword
from app.integrations.crawler.media_crawler_runner import get_crawler
from app.models.content import CrawledContent
from app.schemas.content import ContentOut, SearchRequest, TrendingRequest
from app.services.heat_scoring import tag_items

router = APIRouter(prefix="/api/content", tags=["content"])


# 支持的国内平台
DOMESTIC_PLATFORMS = [
    "xiaohongshu", "douyin", "bilibili", "kuaishou",
    "weibo", "tieba", "zhihu",
]
# 国外平台（暂时通过自建适配器或官方 API，未内置到 MediaCrawler）
INTERNATIONAL_PLATFORMS = ["tiktok", "youtube", "x"]


@router.get("/platforms")
async def list_platforms():
    return {
        "domestic": DOMESTIC_PLATFORMS,
        "international": INTERNATIONAL_PLATFORMS,
    }


@router.post("/search", response_model=List[ContentOut])
async def search(
    req: SearchRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """搜索并落库，返回结果。"""
    try:
        crawler = get_crawler(req.platform)
    except (ValueError, NotImplementedError) as e:
        raise HTTPException(400, detail=str(e))

    raw_items = await crawler.search_by_keyword(req.keyword, limit=req.limit, sort=req.sort)
    if not raw_items:
        return []

    # 打 heat_tag
    tagged = tag_items(raw_items)

    # 关键词趋势分析（AI 一句话）
    try:
        insight = await analyze_keyword(
            req.keyword,
            req.platform,
            [it.get("title", "") for it in tagged],
        )
    except Exception:
        insight = ""

    # 落库
    saved = []
    for it in tagged:
        obj = CrawledContent(
            platform=req.platform,
            source_id=it.get("source_id", ""),
            source_url=it.get("source_url", ""),
            author_name=it.get("author_name", ""),
            author_id=it.get("author_id", ""),
            title=it.get("title", ""),
            content_text=it.get("content_text", ""),
            media_type=it.get("media_type", "text"),
            images=it.get("images", []),
            video_url=it.get("video_url", ""),
            video_cover=it.get("video_cover", ""),
            likes=it.get("likes", 0),
            comments=it.get("comments", 0),
            shares=it.get("shares", 0),
            views=it.get("views", 0),
            heat_score=it.get("heat_score", 0.0),
            heat_tag=it.get("heat_tag", "normal"),
            search_keyword=req.keyword,
            keyword_insight=insight,
            published_at=it.get("published_at"),
        )
        db.add(obj)
        saved.append(obj)
    await db.commit()
    for obj in saved:
        await db.refresh(obj)

    return saved


@router.post("/trending", response_model=List[ContentOut])
async def trending(
    req: TrendingRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    try:
        crawler = get_crawler(req.platform)
    except (ValueError, NotImplementedError) as e:
        raise HTTPException(400, detail=str(e))

    raw_items = await crawler.fetch_trending(limit=req.limit)
    tagged = tag_items(raw_items)

    saved = []
    for it in tagged:
        obj = CrawledContent(
            platform=req.platform,
            source_id=it.get("source_id", ""),
            source_url=it.get("source_url", ""),
            author_name=it.get("author_name", ""),
            title=it.get("title", ""),
            content_text=it.get("content_text", ""),
            media_type=it.get("media_type", "text"),
            images=it.get("images", []),
            video_url=it.get("video_url", ""),
            video_cover=it.get("video_cover", ""),
            likes=it.get("likes", 0),
            comments=it.get("comments", 0),
            shares=it.get("shares", 0),
            views=it.get("views", 0),
            heat_score=it.get("heat_score", 0.0),
            heat_tag=it.get("heat_tag", "normal"),
            search_keyword="__trending__",
        )
        db.add(obj)
        saved.append(obj)
    await db.commit()
    for obj in saved:
        await db.refresh(obj)
    return saved


@router.get("/list", response_model=List[ContentOut])
async def list_contents(
    platform: Optional[str] = None,
    heat_tag: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    q = select(CrawledContent)
    if platform:
        q = q.where(CrawledContent.platform == platform)
    if heat_tag:
        q = q.where(CrawledContent.heat_tag == heat_tag)
    if keyword:
        q = q.where(CrawledContent.search_keyword == keyword)
    q = q.order_by(desc(CrawledContent.heat_score)).limit(limit)

    result = await db.execute(q)
    return list(result.scalars().all())


@router.get("/{content_id}", response_model=ContentOut)
async def get_content(
    content_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    obj = await db.get(CrawledContent, content_id)
    if not obj:
        raise HTTPException(404)
    return obj
