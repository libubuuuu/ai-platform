"""MediaCrawler 统一调度入口。

MediaCrawler 通过 subprocess 调用（它原本是 CLI 工具），
结果从它的输出目录读取 JSON/CSV 后解析。

vendor 路径：backend/vendor/MediaCrawler
执行示例：
    python main.py --platform xhs --type search --keywords "穿搭" --pages 5

注意事项：
- MediaCrawler 需要先通过 `python main.py --platform xhs --type login` 扫码登录
- 登录后 Cookie 缓存到 MediaCrawler/browser_data 目录
- 频率限制：我们在调用前 sleep，尊重 settings.CRAWL_MIN_DELAY_SEC
"""
import asyncio
import json
import random
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

from loguru import logger

from app.core.config import get_settings
from app.integrations.crawler.base import BaseCrawler

settings = get_settings()

# MediaCrawler 的安装位置
VENDOR_ROOT = Path(__file__).resolve().parents[3] / "vendor" / "MediaCrawler"

# MediaCrawler 平台代号映射到我们系统的平台名
PLATFORM_CODE_MAP = {
    "xiaohongshu": "xhs",
    "douyin": "dy",
    "bilibili": "bili",
    "kuaishou": "ks",
    "weibo": "wb",
    "tieba": "tieba",
    "zhihu": "zhihu",
}


class MediaCrawlerRunner(BaseCrawler):
    """基于 MediaCrawler 的统一抓取器。"""

    def __init__(self, platform: str):
        if platform not in PLATFORM_CODE_MAP:
            raise ValueError(f"MediaCrawler 不支持平台：{platform}")
        self.platform_name = platform
        self.platform_code = PLATFORM_CODE_MAP[platform]

    async def _run_cli(self, args: List[str]) -> Dict[str, Any]:
        """执行 MediaCrawler CLI 命令。

        返回它的输出路径（MediaCrawler 把结果写到 data/ 目录）。
        """
        if not VENDOR_ROOT.exists():
            raise RuntimeError(
                f"MediaCrawler 未安装：{VENDOR_ROOT}\n"
                "请先运行：git submodule update --init --recursive"
            )

        # 限速
        delay = random.uniform(
            settings.CRAWL_MIN_DELAY_SEC,
            settings.CRAWL_MAX_DELAY_SEC,
        )
        await asyncio.sleep(delay)

        cmd = [sys.executable, "main.py"] + args
        logger.info(f"[MediaCrawler] 执行：{' '.join(cmd)} (cwd={VENDOR_ROOT})")

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(VENDOR_ROOT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            logger.error(f"[MediaCrawler] 执行失败：{stderr.decode()}")
            raise RuntimeError(f"MediaCrawler 执行失败：{stderr.decode()[:500]}")

        return {"stdout": stdout.decode(), "stderr": stderr.decode()}

    def _parse_output_dir(self) -> List[Dict[str, Any]]:
        """从 MediaCrawler 的 data 目录读取 JSON 结果并标准化。

        MediaCrawler 的默认输出路径是 data/<platform>/*.json。
        字段各平台略有差异，这里做归一化。
        """
        data_dir = VENDOR_ROOT / "data" / self.platform_code
        if not data_dir.exists():
            return []

        results = []
        # 找最新一个 JSON
        json_files = sorted(data_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not json_files:
            return []

        with open(json_files[0], "r", encoding="utf-8") as f:
            raw = json.load(f)

        # 各平台字段不同，这里做通用映射（不完整，需要针对每个平台细化）
        for item in (raw if isinstance(raw, list) else raw.get("data", [])):
            results.append(self._normalize_item(item))

        return results

    def _normalize_item(self, item: dict) -> Dict[str, Any]:
        """把各平台原始字段映射到统一字段。

        TODO：这是最小实现，需要按每个平台扩展。
        你可以先对接 1-2 个平台（比如小红书/抖音），其他之后再补。
        """
        # 通用字段尝试
        return {
            "source_id": str(item.get("id") or item.get("note_id") or item.get("aweme_id") or ""),
            "source_url": item.get("url", "") or item.get("share_url", ""),
            "title": item.get("title") or item.get("desc", "")[:200],
            "content_text": item.get("desc") or item.get("content") or "",
            "author_name": (item.get("user") or {}).get("nickname", "") or item.get("nickname", ""),
            "author_id": (item.get("user") or {}).get("user_id", "") or item.get("user_id", ""),
            "media_type": self._infer_media_type(item),
            "images": item.get("image_list") or item.get("images") or [],
            "video_url": item.get("video_url", "") or (item.get("video") or {}).get("play_addr", ""),
            "video_cover": item.get("cover_url", "") or (item.get("video") or {}).get("cover", ""),
            "likes": int(item.get("liked_count") or item.get("digg_count") or 0),
            "comments": int(item.get("comment_count") or 0),
            "shares": int(item.get("share_count") or 0),
            "views": int(item.get("view_count") or item.get("play_count") or 0),
        }

    @staticmethod
    def _infer_media_type(item: dict) -> str:
        if item.get("video_url") or (item.get("video") and (item.get("video") or {}).get("play_addr")):
            return "video"
        images = item.get("image_list") or item.get("images") or []
        if images:
            return "image" if len(images) == 1 else "mixed"
        return "text"

    async def search_by_keyword(
        self,
        keyword: str,
        limit: int = 20,
        sort: str = "hot",
    ) -> List[Dict[str, Any]]:
        await self._run_cli([
            "--platform", self.platform_code,
            "--type", "search",
            "--keywords", keyword,
            "--get_comment", "no",
        ])
        items = self._parse_output_dir()
        return items[:limit]

    async def fetch_trending(self, limit: int = 20) -> List[Dict[str, Any]]:
        # MediaCrawler 本身没有统一"热门"入口，各平台不同
        # 小红书/抖音走 --type search 带热门关键词近似模拟
        # 这里给个最小实现，实际你可以用关键词"热门" + sort=hot 近似
        return await self.search_by_keyword("热门", limit=limit)

    async def fetch_detail(self, source_id: str) -> Dict[str, Any]:
        await self._run_cli([
            "--platform", self.platform_code,
            "--type", "detail",
            "--note_id", source_id,
        ])
        items = self._parse_output_dir()
        return items[0] if items else {}


def get_crawler(platform: str) -> BaseCrawler:
    """工厂函数：根据平台名返回抓取器实例。"""
    if platform in PLATFORM_CODE_MAP:
        return MediaCrawlerRunner(platform)
    raise NotImplementedError(f"暂不支持平台：{platform}")
