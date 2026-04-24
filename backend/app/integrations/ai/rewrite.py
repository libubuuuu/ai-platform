"""洗稿服务：把抓取内容改写成新内容。"""
import json
from typing import List, Dict, Any

from loguru import logger

from app.integrations.ai.client import ai
from app.integrations.ai.prompts import (
    REWRITE_SINGLE_PROMPT_SYSTEM,
    REWRITE_SINGLE_PROMPT_USER,
    REWRITE_MERGE_PROMPT_SYSTEM,
    REWRITE_MERGE_PROMPT_USER,
    KEYWORD_INSIGHT_PROMPT_SYSTEM,
    KEYWORD_INSIGHT_PROMPT_USER,
    COMMENT_COMMON_PROMPT_SYSTEM,
    COMMENT_COMMON_PROMPT_USER,
)


def _safe_parse_json(text: str) -> dict:
    """兼容 AI 返回带 ```json ``` 包裹的情况。"""
    t = text.strip()
    if t.startswith("```"):
        # 去掉首尾的代码块标记
        lines = t.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        logger.warning(f"AI 返回非 JSON，原文：{text[:200]}")
        return {"title": "", "content": text}


async def rewrite_single(
    source: Dict[str, Any],
    target_platform: str,
) -> Dict[str, str]:
    """对单篇内容洗稿。"""
    user_msg = REWRITE_SINGLE_PROMPT_USER.format(
        platform=target_platform,
        title=source.get("title", ""),
        content=source.get("content_text", ""),
    )
    raw = await ai.chat(REWRITE_SINGLE_PROMPT_SYSTEM, user_msg)
    parsed = _safe_parse_json(raw)
    return {
        "title": parsed.get("title", ""),
        "content": parsed.get("content", ""),
    }


async def rewrite_merge(
    sources: List[Dict[str, Any]],
    target_platform: str,
) -> Dict[str, str]:
    """多篇合并洗稿。"""
    articles_text = "\n\n".join(
        f"【参考{i+1}】标题：{s.get('title','')}\n正文：{s.get('content_text','')}"
        for i, s in enumerate(sources)
    )
    user_msg = REWRITE_MERGE_PROMPT_USER.format(
        platform=target_platform,
        articles=articles_text,
    )
    raw = await ai.chat(REWRITE_MERGE_PROMPT_SYSTEM, user_msg)
    parsed = _safe_parse_json(raw)
    return {
        "title": parsed.get("title", ""),
        "content": parsed.get("content", ""),
    }


async def analyze_keyword(
    keyword: str,
    platform: str,
    sample_titles: List[str],
) -> str:
    """对搜索词做一句话趋势分析。"""
    user_msg = KEYWORD_INSIGHT_PROMPT_USER.format(
        keyword=keyword,
        platform=platform,
        titles="\n".join(f"- {t}" for t in sample_titles[:10]),
    )
    return (await ai.chat(KEYWORD_INSIGHT_PROMPT_SYSTEM, user_msg)).strip()


async def generate_comments(
    bloggers_info: str,
) -> Dict[str, Any]:
    """基于博主群画像生成评论（功能5）。"""
    user_msg = COMMENT_COMMON_PROMPT_USER.format(bloggers_info=bloggers_info)
    raw = await ai.chat(COMMENT_COMMON_PROMPT_SYSTEM, user_msg)
    return _safe_parse_json(raw)
