from __future__ import annotations

import hashlib
import os
import threading
import uuid
from datetime import datetime, timezone
from itertools import cycle
from typing import Any, Dict, List, Optional

OWNER_ACCESS_TOKEN = os.getenv("OWNER_ACCESS_TOKEN", "owner-demo-token")

LOCK = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slugify(value: str) -> str:
    value = value.strip().lower()
    chars = []
    for ch in value:
        chars.append(ch if ch.isalnum() else "-")
    slug = "".join(chars)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "item"


def _stable_score(*parts: str) -> int:
    digest = hashlib.sha256("::".join(parts).encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


PLATFORMS: List[Dict[str, Any]] = [
    {"id": "xiaohongshu", "name": "Xiaohongshu", "region": "domestic", "supports": ["text", "image", "video", "mixed"], "audience": "Lifestyle, product discovery, consumer decisions", "note": "Strong for image-led and short-form content.", "source_hint": "Public discovery feed and saved-note trends"},
    {"id": "douyin", "name": "Douyin", "region": "domestic", "supports": ["video", "mixed", "text", "image"], "audience": "Short video traffic, live commerce, fast trend spread", "note": "Best for punchy hooks and quick cuts.", "source_hint": "Trending list, recommendation feed, creator clips"},
    {"id": "weixin-official", "name": "WeChat Official Account", "region": "domestic", "supports": ["text", "image", "mixed"], "audience": "Deep content, brand retention, conversion support", "note": "Good for long-form and article-style content.", "source_hint": "Article pages, repost chains, historical viral posts"},
    {"id": "wechat-channel", "name": "WeChat Channels", "region": "domestic", "supports": ["video", "mixed", "text"], "audience": "WeChat ecosystem short video and private traffic", "note": "Good for social and community-linked content.", "source_hint": "Recommendation feed, topic pages, live replays"},
    {"id": "kuaishou", "name": "Kuaishou", "region": "domestic", "supports": ["video", "mixed", "text"], "audience": "Community content, live streaming, strong interaction", "note": "Well suited for continuous updates and live content.", "source_hint": "Hot recommendations, creator pages, topic challenges"},
    {"id": "zhihu", "name": "Zhihu", "region": "domestic", "supports": ["text", "image", "video", "mixed"], "audience": "Knowledge, opinions, search traffic", "note": "Good for structured answers and expert content.", "source_hint": "Hot list, question pages, columns and articles"},
    {"id": "tieba", "name": "Tieba", "region": "domestic", "supports": ["text", "image", "video", "mixed"], "audience": "Interest communities and discussion-led content", "note": "Good for topic discussion and community activation.", "source_hint": "Hot posts, pinned threads, reply chains"},
    {"id": "bilibili", "name": "Bilibili", "region": "domestic", "supports": ["video", "mixed", "image", "text"], "audience": "Young users, long/short video, knowledge and entertainment", "note": "Great for scripted video with a clear structure.", "source_hint": "Trending charts, creator pages, comments"},
    {"id": "x", "name": "X", "region": "overseas", "supports": ["text", "image", "video", "mixed"], "audience": "Real-time trends, topic spread, opinion content", "note": "Good for short posts and chained amplification.", "source_hint": "Trending topics, hashtags, repost chains"},
    {"id": "youtube", "name": "YouTube", "region": "overseas", "supports": ["video", "mixed", "text", "image"], "audience": "Long and short video, search traffic, education", "note": "Best as a primary video surface with strong thumbnails.", "source_hint": "Trending, channel pages, recommended videos"},
    {"id": "tiktok", "name": "TikTok", "region": "overseas", "supports": ["video", "mixed", "text", "image"], "audience": "Short video, challenges, viral distribution", "note": "Good for fast, visual, highly engaging content.", "source_hint": "For You, tags, challenge charts"},
]


ACCOUNTS: List[Dict[str, Any]] = [
    {"id": "acc-xhs-brand", "platform_id": "xiaohongshu", "display_name": "Brand Content", "handle": "@brand_lab", "status": "connected", "draft_count": 3, "last_sync": _now(), "owner_only": True},
    {"id": "acc-douyin-main", "platform_id": "douyin", "display_name": "Douyin Main", "handle": "@main_show", "status": "connected", "draft_count": 5, "last_sync": _now(), "owner_only": True},
    {"id": "acc-youtube-studio", "platform_id": "youtube", "display_name": "YouTube Studio", "handle": "@studio_channel", "status": "connected", "draft_count": 2, "last_sync": _now(), "owner_only": True},
]


STATE: Dict[str, Any] = {
    "cart": [],
    "remix_jobs": {},
    "canvas_jobs": {},
    "drafts": [],
    "comment_jobs": {},
    "activity_log": [],
}


def log_activity(action: str, payload: Dict[str, Any]) -> None:
    with LOCK:
        STATE["activity_log"].append({"action": action, "payload": payload, "timestamp": _now()})


def get_platforms(region: Optional[str] = None) -> List[Dict[str, Any]]:
    if region:
        return [item for item in PLATFORMS if item["region"] == region]
    return PLATFORMS


def get_platform(platform_id: str) -> Optional[Dict[str, Any]]:
    return next((item for item in PLATFORMS if item["id"] == platform_id), None)


def get_accounts(platform_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if platform_id:
        return [item for item in ACCOUNTS if item["platform_id"] == platform_id]
    return ACCOUNTS


def connect_account(platform_id: str, display_name: str, handle: str) -> Dict[str, Any]:
    platform = get_platform(platform_id)
    if not platform:
        raise ValueError("Unknown platform")

    account = {
        "id": f"acc-{uuid.uuid4().hex[:10]}",
        "platform_id": platform_id,
        "display_name": display_name,
        "handle": handle,
        "status": "connected",
        "draft_count": 0,
        "last_sync": _now(),
        "owner_only": True,
    }
    with LOCK:
        ACCOUNTS.insert(0, account)
    log_activity("connect_account", {"account_id": account["id"], "platform_id": platform_id})
    return account


def _choose_content_type(platform: Dict[str, Any], index: int) -> str:
    supported = platform["supports"]
    return supported[index % len(supported)]


def _build_media(content_type: str, keyword: str, platform: Dict[str, Any], index: int) -> List[str]:
    slug = _slugify(keyword)
    base = f"https://assets.example.com/{platform['id']}/{slug}/{index + 1}"
    if content_type == "text":
        return []
    if content_type == "image":
        return [f"{base}.jpg"]
    if content_type == "video":
        return [f"{base}.mp4"]
    return [f"{base}.jpg", f"{base}.mp4"]


def build_radar_items(region: str, platform_id: Optional[str], keyword: str, limit: int) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    keyword = keyword.strip() or "trend"
    platforms = get_platforms(region)
    if platform_id:
        filtered = [item for item in platforms if item["id"] == platform_id]
        if filtered:
            platforms = filtered
    if not platforms:
        platforms = get_platforms(region)

    items: List[Dict[str, Any]] = []
    type_counts = {"text": 0, "image": 0, "video": 0, "mixed": 0}
    spread_template = ["source post", "creator follow-up", "comment expansion", "cross-community remix"]

    platform_cycle = cycle(platforms)
    for index in range(limit):
        platform = next(platform_cycle)
        content_type = _choose_content_type(platform, index)
        type_counts[content_type] += 1
        score_seed = _stable_score(region, platform["id"], keyword, str(index))
        potential = 74 + (score_seed % 23)
        freshness_labels = ["live", "24h", "7d"]
        freshness = freshness_labels[index % len(freshness_labels)]
        title = f"{keyword} - {platform['name']} sample {index + 1}"
        summary = (
            f"Content on {platform['name']} around '{keyword}' is likely to be saved and shared, "
            f"and can be repackaged as {content_type}."
        )
        why_hot = (
            "The trend is usually driven by a strong hook, follow-up comments, "
            f"and remix-friendly formats. The main source surface is {platform['source_hint']}."
        )
        items.append(
            {
                "id": f"radar-{platform['id']}-{_slugify(keyword)}-{index + 1}",
                "platform_id": platform["id"],
                "platform_name": platform["name"],
                "region": region,
                "title": title,
                "summary": summary,
                "source_name": platform["source_hint"],
                "source_url": f"https://example.com/{platform['id']}/{_slugify(keyword)}/{index + 1}",
                "content_type": content_type,
                "why_hot": why_hot,
                "spread_path": spread_template,
                "potential_score": potential,
                "freshness": freshness,
                "prompt_seed": f"{keyword} / {platform['name']} / {content_type} / {freshness}",
                "media": _build_media(content_type, keyword, platform, index),
                "created_at": _now(),
            }
        )

    insights = {
        "analysis": (
            f"Primary source surface: {platforms[0]['source_hint']}. "
            "Typical spread goes from the source post to creator amplification, then comments and remixes."
        ),
        "trend_reason": f"Keyword '{keyword}' maps to multiple platform scenarios and can power a content matrix.",
        "content_mix": type_counts,
        "source_hint": platforms[0]["source_hint"],
    }
    log_activity("build_radar_items", {"region": region, "platform_id": platform_id, "keyword": keyword, "limit": limit})
    return items, insights


def _rewrite_from_sources(sources: List[Dict[str, Any]], tone: str, preserve_media: bool, mode: str) -> Dict[str, Any]:
    if not sources:
        raise ValueError("At least one source item is required")

    source_titles = [item["title"] for item in sources]
    source_labels = [f"{item['platform_name']} / {item['content_type']}" for item in sources]
    keyword = sources[0]["title"].split(" - ")[0]

    if mode == "one_by_one":
        drafts = []
        for index, item in enumerate(sources, start=1):
            drafts.append(
                {
                    "draft_id": f"draft-{uuid.uuid4().hex[:10]}",
                    "title": f"{item['title']} - rewrite",
                    "text": (
                        f"Reframe {item['title']} in a {tone} tone, keep the core idea, "
                        "and restructure it for a single-post release."
                    ),
                    "source_id": item["id"],
                    "source_title": item["title"],
                    "media_plan": item["media"] if preserve_media else [],
                    "position": index,
                }
            )
        return {"drafts": drafts, "summary": f"Generated {len(drafts)} separate rewrite drafts."}

    merged_text = (
        f"Built a {tone} composite draft around '{keyword}' using {len(sources)} sources. "
        f"It combines {', '.join(source_labels)} into one structure with shared hooks, examples, and actions."
    )
    if mode == "rewrite":
        merged_text += " The structure is tighter and better suited for a single post."
    else:
        merged_text += " The result is suitable for series distribution and a content matrix."

    media_plan = []
    if preserve_media:
        for item in sources:
            media_plan.extend(item["media"])

    return {
        "drafts": [
            {
                "draft_id": f"draft-{uuid.uuid4().hex[:10]}",
                "title": f"{sources[0]['title']} - composite version",
                "text": merged_text,
                "source_ids": [item["id"] for item in sources],
                "source_titles": source_titles,
                "media_plan": media_plan,
            }
        ],
        "summary": f"Generated 1 {mode} draft.",
    }


def create_remix_job(request: Dict[str, Any], sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    job_id = f"remix-{uuid.uuid4().hex[:10]}"
    result = _rewrite_from_sources(
        sources=sources,
        tone=request["tone"],
        preserve_media=request["preserve_media"],
        mode=request["mode"],
    )
    job = {
        "job_id": job_id,
        "status": "completed",
        "mode": request["mode"],
        "tone": request["tone"],
        "preserve_media": request["preserve_media"],
        "sources": [
            {
                "id": item["id"],
                "title": item["title"],
                "platform_name": item["platform_name"],
                "content_type": item["content_type"],
                "source_url": item["source_url"],
            }
            for item in sources
        ],
        "drafts": result["drafts"],
        "summary": result["summary"],
        "created_at": _now(),
    }
    with LOCK:
        STATE["remix_jobs"][job_id] = job
    log_activity("create_remix_job", {"job_id": job_id, "source_count": len(sources)})
    return job


def create_canvas_job(request: Dict[str, Any]) -> Dict[str, Any]:
    job_id = f"canvas-{uuid.uuid4().hex[:10]}"
    base_prompt = f"{request['prompt_hint']} | {request['style']} | {request['image_name']}"
    variants = []
    for index in range(request["count"]):
        variants.append(
            {
                "id": f"{job_id}-{index + 1}",
                "prompt": f"{base_prompt} | similarity {90 - index * 5}%",
                "style": f"{request['style']} variant {index + 1}",
                "note": "You can extract this prompt again and feed it into the next pass.",
                "score": 91 - index * 4,
            }
        )

    job = {
        "job_id": job_id,
        "status": "completed",
        "image_name": request["image_name"],
        "prompt_hint": request["prompt_hint"],
        "style": request["style"],
        "variants": variants,
        "created_at": _now(),
    }
    with LOCK:
        STATE["canvas_jobs"][job_id] = job
    log_activity("create_canvas_job", {"job_id": job_id, "count": request["count"]})
    return job


def create_draft(request: Dict[str, Any], account: Dict[str, Any], platform: Dict[str, Any]) -> Dict[str, Any]:
    draft = {
        "id": f"publish-{uuid.uuid4().hex[:10]}",
        "platform_id": request["platform_id"],
        "platform_name": platform["name"],
        "account_id": request["account_id"],
        "account_name": account["display_name"],
        "handle": account["handle"],
        "title": request["title"],
        "body": request["body"],
        "source_ids": request.get("source_ids", []),
        "media": request.get("media", []),
        "target": request.get("target", "draft"),
        "notes": request.get("notes", ""),
        "status": "saved",
        "created_at": _now(),
    }
    with LOCK:
        STATE["drafts"].insert(0, draft)
    log_activity("create_draft", {"draft_id": draft["id"], "account_id": account["id"]})
    return draft


def create_comment_suggestions(request: Dict[str, Any]) -> Dict[str, Any]:
    targets = request["targets"] or ["Target A", "Target B"]
    shared_points = [
        "Shared point 1: the opening line emphasizes a clear benefit.",
        "Shared point 2: each post invites follow-up in the comment section.",
        "Shared point 3: the titles use a strong verb and a specific scene.",
    ]
    suggestions = []
    for target in targets[:5]:
        suggestions.append(
            {
                "target": target,
                "comment": (
                    f"Strong point on {target}. You can extend this with one more actionable step "
                    f"to keep the {request['tone']} tone."
                ),
                "angle": f"follow-up suggestion for {target}",
            }
        )

    job = {
        "job_id": f"comment-{uuid.uuid4().hex[:10]}",
        "targets": targets,
        "context": request["context"],
        "tone": request["tone"],
        "shared_points": shared_points,
        "suggestions": suggestions,
        "safety_note": "Only comment suggestions are produced. Human review is required before posting.",
        "created_at": _now(),
    }
    with LOCK:
        STATE["comment_jobs"][job["job_id"]] = job
    log_activity("create_comment_suggestions", {"target_count": len(targets)})
    return job


def validate_owner_token(token: str) -> bool:
    return token == OWNER_ACCESS_TOKEN


def get_overview() -> Dict[str, Any]:
    return {
        "platform_count": len(PLATFORMS),
        "domestic_count": len([item for item in PLATFORMS if item["region"] == "domestic"]),
        "overseas_count": len([item for item in PLATFORMS if item["region"] == "overseas"]),
        "connected_accounts": len(ACCOUNTS),
        "draft_count": len(STATE["drafts"]),
        "remix_jobs": len(STATE["remix_jobs"]),
        "canvas_jobs": len(STATE["canvas_jobs"]),
    }
