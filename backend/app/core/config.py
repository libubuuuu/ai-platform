"""应用配置：从 .env 读取，全局单例。"""
from functools import lru_cache
from typing import List, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "AI Platform"
    DEBUG: bool = False
    SECRET_KEY: str = Field(..., min_length=16)

    # DB
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_platform.db"

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = Field(..., min_length=6)

    # AI
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.deepseek.com"
    OPENAI_MODEL: str = "deepseek-chat"
    DEFAULT_AI_PROVIDER: Literal["anthropic", "openai"] = "openai"

    # ComfyUI
    COMFYUI_BASE_URL: str = "http://127.0.0.1:8188"
    COMFYUI_ENABLED: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Rate limits
    CRAWL_MIN_DELAY_SEC: int = 2
    CRAWL_MAX_DELAY_SEC: int = 5
    CRAWL_MAX_CONCURRENT: int = 1
    PUBLISH_MIN_DELAY_SEC: int = 30
    PUBLISH_MAX_DELAY_SEC: int = 120
    PUBLISH_DEFAULT_TO_DRAFT: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
