from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── Database ────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://vtb:vtbpassword@localhost:5432/vtb"
    db_pool_min_size: int = 5
    db_pool_max_size: int = 20
    db_pool_max_overflow: int = 10

    # ── Redis ───────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 50
    cache_ttl_seconds: int = 900          # 15 min for feeds and detail pages
    search_cache_ttl_seconds: int = 300   # 5 min for search (more unique keys)
    health_cache_ttl_seconds: int = 30    # 30 s for /health

    # ── Ollama / LLM ────────────────────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma4:26b"
    ollama_timeout: float = 600.0

    # ── API ─────────────────────────────────────────────────────────────────
    pipeline_api_key: str = "change-me-in-production"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "https://viewtheboard.vercel.app",
    ]

    # ── Rate limits (requests per minute per IP) ─────────────────────────────
    rate_limit_default: str = "60/minute"
    rate_limit_search: str = "30/minute"
    rate_limit_pipeline: str = "10/minute"


settings = Settings()
