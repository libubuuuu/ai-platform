"""发布集成层：封装 social-auto-upload 为统一接口。

核心原则：
1. 默认只发到草稿箱（target="draft"），不自动公开
2. 每次发布前随机延迟，避免高频被风控
3. 每个账号使用独立的 storage_state 和代理
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BasePublisher(ABC):
    """发布器基类。"""

    platform_name: str = ""

    @abstractmethod
    async def publish_to_draft(
        self,
        account: Dict[str, Any],    # PlatformAccount 的 dict
        content: Dict[str, Any],    # RewrittenContent 的 dict
    ) -> Dict[str, Any]:
        """发布到草稿箱。

        返回：
        {
          "success": bool,
          "draft_id": str | None,
          "message": str,
          "raw": dict  # 平台原始响应
        }
        """
        ...

    @abstractmethod
    async def check_login(self, account: Dict[str, Any]) -> bool:
        """检查账号登录态是否有效。"""
        ...
