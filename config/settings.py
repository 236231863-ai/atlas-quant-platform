"""
Atlas Quant Platform - Configuration.

基于 pydantic-settings 的配置管理。
"""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="atlas_db_")
    url: str = "sqlite+aiosqlite:///data/atlas.db"
    echo: bool = False
    pool_size: int = 5


class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="atlas_log_")
    level: str = "INFO"
    file: str | None = None


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="atlas_ai_")
    default_provider: str = "openai"
    openai_api_key: str = Field(default="", exclude=True)
    anthropic_api_key: str = Field(default="", exclude=True)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="atlas_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
    )
    db: DatabaseSettings = DatabaseSettings()
    logging: LoggingSettings = LoggingSettings()
    ai: AISettings = AISettings()
    debug: bool = False
    environment: str = "development"


settings = AppSettings()
