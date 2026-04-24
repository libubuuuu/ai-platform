"""平台账号表：存各平台的登录态（Cookie/Session）。

⚠️ 注意：Cookie 敏感，存储时建议加密（当前未加密，生产环境请启用 Fernet 加密）。
"""
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PlatformAccount(Base):
    __tablename__ = "platform_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # 平台：douyin / xiaohongshu / bilibili / kuaishou / wechat_channel /
    #       baijiahao / tiktok / youtube / x / ...
    platform: Mapped[str] = mapped_column(String(32), index=True)

    # 账号显示名（用户自定义，便于识别）
    display_name: Mapped[str] = mapped_column(String(128))

    # 登录态：Cookie 字符串或 Playwright storage_state JSON
    cookies: Mapped[str] = mapped_column(Text, default="")
    storage_state: Mapped[dict] = mapped_column(JSON, default=dict)

    # 代理配置（每个账号独立 IP）
    proxy_url: Mapped[str] = mapped_column(String(256), default="")
    # User-Agent 指纹
    user_agent: Mapped[str] = mapped_column(String(512), default="")

    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
