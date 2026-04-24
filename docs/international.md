# 国外平台对接说明

## 当前状态

| 平台 | 抓取（功能1） | 发布（功能4） |
|------|--------------|---------------|
| TikTok  | ⚠️ 未内置（建议官方 Research API） | ✅ via SAU |
| YouTube | ⚠️ 未内置（建议 YouTube Data API） | ⚠️ 推荐官方 API |
| X       | ⚠️ 未内置（建议 X API v2） | ⚠️ 推荐官方 API |

## 为什么不用爬虫做国外平台？

- **TikTok**: 风控团队规模庞大，住宅 IP + 真机指纹也未必稳定。爬虫维护成本高，建议申请 [TikTok Research API](https://developers.tiktok.com/products/research-api/)（需学术/媒体身份）。
- **YouTube**: 官方 API 完全够用，免费额度 10,000 单位/天，能查询、上传、管理评论。
- **X**: 2024 年起对爬虫极度敌视，封号速度以分钟计。Basic 套餐 $200/月起，但合规且稳定。

## 如何在本系统中扩展国外平台

### 抓取扩展

1. 在 `backend/app/integrations/crawler/` 下新建 `tiktok_official.py`
2. 继承 `BaseCrawler`，实现 `search_by_keyword` 等方法
3. 在 `media_crawler_runner.get_crawler` 工厂函数中加分支

骨架示例：

```python
# backend/app/integrations/crawler/youtube_official.py
import httpx
from app.integrations.crawler.base import BaseCrawler

class YouTubeCrawler(BaseCrawler):
    platform_name = "youtube"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search_by_keyword(self, keyword, limit=20, sort="hot"):
        async with httpx.AsyncClient() as c:
            r = await c.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "key": self.api_key,
                    "q": keyword,
                    "part": "snippet",
                    "maxResults": limit,
                    "order": "viewCount" if sort == "hot" else "date",
                    "type": "video",
                },
            )
            data = r.json()
            return [self._normalize(item) for item in data.get("items", [])]

    def _normalize(self, item):
        s = item["snippet"]
        return {
            "source_id": item["id"]["videoId"],
            "source_url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            "title": s["title"],
            "content_text": s["description"],
            "author_name": s["channelTitle"],
            "media_type": "video",
            "video_cover": s["thumbnails"]["high"]["url"],
            # 详细的 likes/views 需要再调 videos.list?part=statistics
        }
    # ... 实现 fetch_trending / fetch_detail
```

然后在 `.env` 中加：
```
YOUTUBE_API_KEY="..."
```

### 发布扩展

YouTube 上传走官方 API（[upload guide](https://developers.google.com/youtube/v3/guides/uploading_a_video)）。
在 `backend/app/integrations/publisher/` 下新建 `youtube_publisher.py`，继承 `BasePublisher`。
