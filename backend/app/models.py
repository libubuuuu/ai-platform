from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

Region = Literal["domestic", "overseas"]
ContentType = Literal["text", "image", "video", "mixed"]
RemixMode = Literal["merge", "rewrite", "one_by_one"]
PublishTarget = Literal["draft", "queue"]


@dataclass
class Platform:
    id: str
    name: str
    region: Region
    supports: list[ContentType]
    audience: str
    note: str
    source_hint: str


@dataclass
class RadarQuery:
    region: Region = "domestic"
    platform_id: Optional[str] = None
    keyword: str = "热点"
    limit: int = 6


@dataclass
class ContentItem:
    id: str
    platform_id: str
    platform_name: str
    region: Region
    title: str
    summary: str
    source_name: str
    source_url: str
    content_type: ContentType
    why_hot: str
    spread_path: list[str] = field(default_factory=list)
    potential_score: int = 0
    freshness: str = ""
    prompt_seed: str = ""
    media: list[str] = field(default_factory=list)
    created_at: str = ""

