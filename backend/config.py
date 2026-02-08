"""Configuration management for AutoSearch AI."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and `.env`."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "AutoSearch AI"
    app_version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    llm_provider: Literal["openai", "ollama", "groq", "together", "custom"] = "openai"
    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.2
    llm_max_tokens: int = 1200

    search_engines: list[str] = Field(default_factory=lambda: ["duckduckgo"])
    search_max_results: int = 8
    search_region: str = "wt-wt"
    search_language: str = "en"
    arxiv_base_url: str = "http://export.arxiv.org/api/query"
    arxiv_categories: list[str] = Field(
        default_factory=lambda: ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "stat.ML"]
    )
    arxiv_min_interval_seconds: float = 3.0
    arxiv_max_results: int = 24

    content_max_pages: int = 6
    content_max_length: int = 3500
    content_timeout: int = 10

    reranker_enabled: bool = True
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_top_k: int = 5

    google_api_key: str | None = None
    google_cx_id: str | None = None
    bing_api_key: str | None = None
    brave_api_key: str | None = None

    cache_enabled: bool = True
    cache_ttl: int = 1800
    cache_max_size: int = 1024

    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )

    @field_validator("search_engines", "cors_origins", "arxiv_categories", mode="before")
    @classmethod
    def parse_list_fields(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                import json

                return json.loads(stripped)
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
