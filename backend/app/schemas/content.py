"""内容相关请求/响应模型。"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ContentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    platform: str
    source_id: str
    source_url: str
    title: str
    content_text: str
    author_name: str
    author_id: str
    media_type: str
    images: List[str]
    video_url: str
    video_cover: str
    likes: int
    comments: int
    shares: int
    views: int
    heat_score: float
    heat_tag: str
    search_keyword: str
    keyword_insight: str
    published_at: Optional[datetime]
    crawled_at: datetime


class SearchRequest(BaseModel):
    platform: str
    keyword: str
    limit: int = 20
    sort: str = "hot"  # hot / latest / rising


class TrendingRequest(BaseModel):
    platform: str
    limit: int = 20


class RewriteRequest(BaseModel):
    content_ids: List[int]
    target_platform: str
    mode: str = "single"  # single | merge


class RewrittenContentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_content_ids: List[int]
    mode: str
    title: str
    content_text: str
    images: List[str]
    video_url: str
    ai_provider: str
    ai_model: str
    created_at: datetime


class CartAddRequest(BaseModel):
    content_id: int


class CartOut(BaseModel):
    count: int
    items: List[ContentOut]
