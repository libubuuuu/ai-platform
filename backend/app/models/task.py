"""发布任务：内容 → 平台账号 → 草稿箱的任务记录。"""
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PublishTask(Base):
    __tablename__ = "publish_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # 要发布的内容
    content_id: Mapped[int] = mapped_column(ForeignKey("rewritten_contents.id"))
    # 发到哪个账号
    account_id: Mapped[int] = mapped_column(ForeignKey("platform_accounts.id"))

    # 状态：pending / running / success / failed
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    # 目标：draft（草稿）/ publish（直接发布，默认禁用）
    target: Mapped[str] = mapped_column(String(16), default="draft")

    # 执行日志
    log: Mapped[str] = mapped_column(Text, default="")
    error_message: Mapped[str] = mapped_column(Text, default="")
    # 平台返回的结果（如 draft_id）
    result: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
