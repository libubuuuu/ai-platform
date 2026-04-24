"""内容热度评分 & 分类。

简单启发式：
- heat_score = log1p(likes) + 2*log1p(comments) + 3*log1p(shares) + 0.5*log1p(views)
- 按 published_at 的新旧加权（越新权重越高）

heat_tag 的划分：
- top 10% → "hot"
- 中上 20% 且近 24h → "rising"
- 极高互动率 + 很新（<3h）→ "predicted_viral"
- 其他 → "normal"
"""
import math
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any


def compute_heat_score(item: Dict[str, Any]) -> float:
    likes = int(item.get("likes") or 0)
    comments = int(item.get("comments") or 0)
    shares = int(item.get("shares") or 0)
    views = int(item.get("views") or 0)

    base = (
        math.log1p(likes)
        + 2 * math.log1p(comments)
        + 3 * math.log1p(shares)
        + 0.5 * math.log1p(views)
    )

    # 时间衰减：发布越久权重越低
    pub = item.get("published_at")
    if pub:
        if isinstance(pub, str):
            try:
                pub = datetime.fromisoformat(pub)
            except ValueError:
                pub = None
    if pub:
        now = datetime.now(timezone.utc) if pub.tzinfo else datetime.now()
        hours = max(0.1, (now - pub).total_seconds() / 3600)
        # 半衰期 48 小时
        time_weight = 0.5 ** (hours / 48)
        base *= (0.5 + 0.5 * time_weight)

    return round(base, 2)


def tag_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """给一批内容打 heat_tag。"""
    if not items:
        return items

    # 1. 先算 heat_score
    for it in items:
        it["heat_score"] = compute_heat_score(it)

    # 2. 排序取阈值
    scores = sorted([it["heat_score"] for it in items], reverse=True)
    n = len(scores)
    top10 = scores[max(0, int(n * 0.1) - 1)] if n >= 10 else scores[0]
    top30 = scores[max(0, int(n * 0.3) - 1)] if n >= 10 else scores[-1]

    now = datetime.now(timezone.utc)

    for it in items:
        score = it["heat_score"]
        pub = it.get("published_at")
        age_hours = None
        if pub:
            if isinstance(pub, str):
                try:
                    pub = datetime.fromisoformat(pub)
                except ValueError:
                    pub = None
        if pub:
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            age_hours = (now - pub).total_seconds() / 3600

        # 预爆：极新（<3h）+ 互动率远超平均
        if age_hours is not None and age_hours < 3 and score >= top30:
            it["heat_tag"] = "predicted_viral"
        elif score >= top10:
            it["heat_tag"] = "hot"
        elif age_hours is not None and age_hours < 24 and score >= top30:
            it["heat_tag"] = "rising"
        else:
            it["heat_tag"] = "normal"

    return items
