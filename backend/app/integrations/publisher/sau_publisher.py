"""social-auto-upload 统一调度。

vendor 路径：backend/vendor/social-auto-upload
原始项目通过 Playwright 自动操作浏览器登录并上传视频到草稿箱。

我们的封装策略：
1. 每个 PlatformAccount 对应一个独立的 Playwright storage_state 文件
2. 调用上游的 uploader 模块时传入该 account 的 storage_state
3. 所有上传默认 target="draft"，哪怕原项目默认公开，我们也强制草稿

⚠️ 当前是骨架：需要你：
- git submodule update 拉取上游
- 调整 sys.path 导入 uploader 模块
- 扫码登录每个账号生成 storage_state
"""
import asyncio
import random
import sys
from pathlib import Path
from typing import Dict, Any

from loguru import logger

from app.core.config import get_settings
from app.integrations.publisher.base import BasePublisher

settings = get_settings()

VENDOR_ROOT = Path(__file__).resolve().parents[3] / "vendor" / "social-auto-upload"

# 平台 → social-auto-upload 的 uploader 模块名
UPLOADER_MAP = {
    "douyin": "uploader.douyin_uploader",
    "xiaohongshu": "uploader.xhs_uploader",
    "wechat_channel": "uploader.tencent_uploader",
    "kuaishou": "uploader.ks_uploader",
    "bilibili": "uploader.bilibili_uploader",
    "baijiahao": "uploader.baijiahao_uploader",
    "tiktok": "uploader.tk_uploader",
}


def _ensure_vendor_on_path():
    """把 social-auto-upload 加入 sys.path。"""
    if not VENDOR_ROOT.exists():
        raise RuntimeError(
            f"social-auto-upload 未安装：{VENDOR_ROOT}\n"
            "运行：git submodule update --init --recursive"
        )
    sys_path = str(VENDOR_ROOT)
    if sys_path not in sys.path:
        sys.path.insert(0, sys_path)


class SocialAutoUploadPublisher(BasePublisher):
    """基于 social-auto-upload 的发布器。"""

    def __init__(self, platform: str):
        if platform not in UPLOADER_MAP:
            raise ValueError(f"social-auto-upload 不支持平台：{platform}")
        self.platform_name = platform

    async def publish_to_draft(
        self,
        account: Dict[str, Any],
        content: Dict[str, Any],
    ) -> Dict[str, Any]:
        """发布到草稿箱。

        :param account: {id, platform, storage_state, proxy_url, cookies, ...}
        :param content: {title, content_text, images, video_url, ...}
        """
        if not settings.PUBLISH_DEFAULT_TO_DRAFT:
            logger.warning("⚠️ PUBLISH_DEFAULT_TO_DRAFT=false，这是危险配置！")

        # 限速：保护账号
        delay = random.uniform(
            settings.PUBLISH_MIN_DELAY_SEC,
            settings.PUBLISH_MAX_DELAY_SEC,
        )
        logger.info(f"[Publisher] 随机延迟 {delay:.1f}s 后发布...")
        await asyncio.sleep(delay)

        _ensure_vendor_on_path()

        try:
            # 骨架实现：真正接入时需要根据每个平台的 uploader 签名调整
            # 下面是示例逻辑，实际会导入具体 uploader 类并调用
            result = await self._publish_dispatch(account, content)
            return {
                "success": True,
                "draft_id": result.get("draft_id"),
                "message": "已保存到草稿箱",
                "raw": result,
            }
        except Exception as e:
            logger.exception(f"[Publisher] 发布失败：{e}")
            return {
                "success": False,
                "draft_id": None,
                "message": str(e),
                "raw": {},
            }

    async def _publish_dispatch(
        self,
        account: Dict[str, Any],
        content: Dict[str, Any],
    ) -> Dict[str, Any]:
        """真正的发布分发逻辑。

        TODO：针对每个平台的 uploader 做具体调用。
        这里先抛 NotImplementedError 作为占位，避免误操作账号。
        你接入具体平台时把对应分支打开即可。
        """
        raise NotImplementedError(
            f"[{self.platform_name}] 发布逻辑骨架未接入。\n"
            "请按 docs/publisher_integration.md 的指引，\n"
            "在 _publish_dispatch 中添加对应平台 uploader 的调用代码。"
        )

    async def check_login(self, account: Dict[str, Any]) -> bool:
        """检查登录态是否有效（访问个人主页看是否重定向到登录页）。"""
        # TODO：每平台一个简单探测逻辑
        return bool(account.get("storage_state") or account.get("cookies"))


def get_publisher(platform: str) -> BasePublisher:
    if platform in UPLOADER_MAP:
        return SocialAutoUploadPublisher(platform)
    raise NotImplementedError(f"暂不支持发布到：{platform}")
