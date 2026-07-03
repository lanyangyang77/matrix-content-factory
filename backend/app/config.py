"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central config for the Matrix Biz Automation System."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Database ---
    database_url: str = "postgresql://user:password@localhost:5432/matrix_biz"

    # --- Redis / Celery ---
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # --- OpenAI / LLM ---
    openai_api_key: str = ""
    openai_model_name: str = "gpt-4o-mini"
    openai_temperature: float = 0.7
    openai_api_base: str = ""

    # --- App ---
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "change-me-to-a-random-secret"


settings = Settings()  # singleton
