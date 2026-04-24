"""抓取集成层：封装 MediaCrawler 为统一接口。

设计思路：
- MediaCrawler 是命令行工具，我们通过 subprocess 调用
- 或者直接 import 它的模块（更推荐，但需要确保路径正确）
- 结果落盘后解析成统一 CrawledContent

这里提供基础抽象，具体平台实现在 adapters 子目录。
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseCrawler(ABC):
    """抓取器基类。所有平台 adapter 都要实现这个接口。"""

    platform_name: str = ""

    @abstractmethod
    async def search_by_keyword(
        self,
        keyword: str,
        limit: int = 20,
        sort: str = "hot",  # hot / latest / rising
    ) -> List[Dict[str, Any]]:
        """按关键词搜索内容。

        返回字段标准化：
        [
          {
            "source_id": str,
            "source_url": str,
            "title": str,
            "content_text": str,
            "author_name": str,
            "author_id": str,
            "media_type": "text"|"image"|"video"|"mixed",
            "images": [url, ...],
            "video_url": str,
            "video_cover": str,
            "likes": int,
            "comments": int,
            "shares": int,
            "views": int,
            "published_at": datetime|None,
          },
          ...
        ]
        """
        ...

    @abstractmethod
    async def fetch_trending(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取当前热门榜单。"""
        ...

    @abstractmethod
    async def fetch_detail(self, source_id: str) -> Dict[str, Any]:
        """抓取单条内容详情（包含评论、完整正文、媒体链接）。"""
        ...
