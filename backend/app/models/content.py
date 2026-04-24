"""内容相关模型：抓取内容 + 洗稿内容。"""
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CrawledContent(Base):
    """抓取到的原始内容。"""
    __tablename__ = "crawled_contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # 来源
    platform: Mapped[str] = mapped_column(String(32), index=True)
    source_id: Mapped[str] = mapped_column(String(128), index=True)  # 平台原 ID
    source_url: Mapped[str] = mapped_column(String(512))

    # 作者
    author_name: Mapped[str] = mapped_column(String(128), default="")
    author_id: Mapped[str] = mapped_column(String(128), default="")

    # 内容
    title: Mapped[str] = mapped_column(String(512), default="")
    content_text: Mapped[str] = mapped_column(Text, default="")
    # 媒体类型：text / image / video / mixed
    media_type: Mapped[str] = mapped_column(String(16), default="text")
    # 图片 URL 列表
    images: Mapped[list] = mapped_column(JSON, default=list)
    # 视频 URL
    video_url: Mapped[str] = mapped_column(String(512), default="")
    video_cover: Mapped[str] = mapped_column(String(512), default="")

    # 数据指标
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    views: Mapped[int] = mapped_column(Integer, default=0)

    # 热度评分（本系统计算）
    heat_score: Mapped[float] = mapped_column(Float, default=0.0)
    # 潜力标签：hot / rising / predicted_viral / normal
    heat_tag: Mapped[str] = mapped_column(String(32), default="normal", index=True)

    # 搜索词来源（哪个关键词搜来的）
    search_keyword: Mapped[str] = mapped_column(String(128), default="", index=True)
    # 关键词的流行度分析（AI 生成的一句话）
    keyword_insight: Mapped[str] = mapped_column(Text, default="")

    # 原发布时间
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    crawled_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class RewrittenContent(Base):
    """AI 洗稿后的内容。"""
    __tablename__ = "rewritten_contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # 源内容 ID 列表（支持"多篇合并洗稿"）
    source_content_ids: Mapped[list] = mapped_column(JSON, default=list)

    # 洗稿模式：single（一对一）/ merge（多合一）
    mode: Mapped[str] = mapped_column(String(16), default="single")

    # 洗稿结果
    title: Mapped[str] = mapped_column(String(512), default="")
    content_text: Mapped[str] = mapped_column(Text, default="")
    # 复刻的图片（可能是原图或 AI 相似生成）
    images: Mapped[list] = mapped_column(JSON, default=list)
    # 复刻的视频（可能是原视频或剪辑版）
    video_url: Mapped[str] = mapped_column(String(512), default="")

    # AI 使用的 provider 和模型
    ai_provider: Mapped[str] = mapped_column(String(32), default="")
    ai_model: Mapped[str] = mapped_column(String(64), default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
