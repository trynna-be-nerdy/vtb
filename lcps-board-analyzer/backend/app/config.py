"""Application configuration — reads from environment variables / .env file."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "LCPS Board Meeting Analyzer"
    app_version: str = "1.0.0"
    debug: bool = False
    api_key: str = "change-me-before-production"

    # Database
    database_url: str = "postgresql+asyncpg://lcps:lcps_dev@localhost:5432/lcps_analyzer"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_cache_ttl: int = 900  # 15 minutes

    # Ollama / Gemma 4
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma4:4b"
    ollama_timeout: int = 120
    gemma_max_retries: int = 2

    # Pipeline
    pipeline_interval_hours: int = 6
    pipeline_request_delay: float = 4.0  # seconds between HTTP requests
    pdf_chunk_max_chars: int = 2000

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # Legistar API (Loudoun County BOS — structured JSON, no scraping needed)
    legistar_base_url: str = "https://webapi.legistar.com/v1/loudoun"


@lru_cache
def get_settings() -> Settings:
    return Settings()
