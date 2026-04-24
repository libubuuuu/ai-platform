"""发布/账号相关 schema。"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class AccountCreateRequest(BaseModel):
    platform: str
    display_name: str
    cookies: str = ""
    proxy_url: str = ""
    user_agent: str = ""


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    platform: str
    display_name: str
    proxy_url: str
    is_active: bool
    last_checked_at: Optional[datetime]
    created_at: datetime


class PublishRequest(BaseModel):
    rewritten_id: int
    account_ids: List[int]
    target: str = "draft"  # 仅允许 draft


class PublishTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_id: int
    account_id: int
    status: str
    target: str
    log: str
    error_message: str
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]


class CommentGenerateRequest(BaseModel):
    """功能 5：输入一批博主 URL，生成评论建议。"""
    blogger_urls: List[str]
    platform: str


class CommentSuggestion(BaseModel):
    common_analysis: str
    target_bloggers: List[dict]
    comments: List[dict]  # [{style, text}]
