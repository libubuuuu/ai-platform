"""功能5：评论区 AI 文案生成（半自动，默认不自动发）。仅 admin 可用。

接收一批博主 URL，抓取他们最近内容，用 AI 分析共同点，
返回：共同点分析 + 适合的博主列表 + 3 种风格的评论文案。

**默认只生成文案，不自动发送。** 用户需要自己复制到评论区。
"""
from fastapi import APIRouter, Depends

from app.core.security import require_admin
from app.integrations.ai.rewrite import generate_comments
from app.schemas.publish import CommentGenerateRequest, CommentSuggestion

router = APIRouter(prefix="/api/comment", tags=["comment", "admin-only"])


@router.post("/suggest", response_model=CommentSuggestion)
async def suggest_comments(
    req: CommentGenerateRequest,
    admin: dict = Depends(require_admin),
):
    # 骨架实现：把 URL 列表拼成描述文本交给 AI
    # 真实使用时应该先抓取每个博主的最近 5 条内容，提炼画像
    bloggers_info = "\n".join(f"- {url}" for url in req.blogger_urls)
    bloggers_info += f"\n平台：{req.platform}"

    result = await generate_comments(bloggers_info)
    return CommentSuggestion(
        common_analysis=result.get("common_analysis", ""),
        target_bloggers=result.get("target_bloggers", []),
        comments=result.get("comments", []),
    )
