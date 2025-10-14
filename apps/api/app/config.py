from functools import lru_cache
from typing import Literal

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    google_routes_api_key: str = Field("", alias="GOOGLE_ROUTES_API_KEY")
    google_places_api_key: str = Field("", alias="GOOGLE_PLACES_API_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    google_ai_api_key: str | None = Field(default=None, alias="GOOGLE_AI_API_KEY")
    llm_provider: Literal["openai", "google", "gpt-oss"] | None = Field(
        default=None, alias="LLM_PROVIDER"
    )
    redis_url: str = Field("redis://redis:6379/0", alias="REDIS_URL")
    database_url: str = Field(
        "postgresql+asyncpg://bifrost:bifrost@db:5432/bifrost", alias="DATABASE_URL"
    )

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
