from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "品牌风险与可见性分析平台"
    api_prefix: str = "/api"
    secret_key: str = "replace-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/geo_gtm_mvp"
    redis_url: str = "redis://redis:6379/0"
    frontend_origin: str = "http://localhost:3000,http://127.0.0.1:3000"

    seed_demo: bool = True
    real_provider_enabled: bool = False
    real_provider_api_key: str | None = None
    run_rate_limit_seconds: int = 60
    brand_topics_limit: int = 6

    reports_dir: Path = Field(default_factory=lambda: Path("/app/generated_reports"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
