"""
Application settings using pydantic-settings.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "postgresql+asyncpg://signal_user:signal_pass@localhost:5432/signal"
    database_sync_url: str = "postgresql+psycopg2://signal_user:signal_pass@localhost:5432/signal"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # External APIs
    tavily_api_key: Optional[str] = None
    thrad_api_key: Optional[str] = None
    overmind_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Meta MCP + Marketing API
    meta_mcp_endpoint: str = "mcp://meta/ads"
    meta_ads_access_token: Optional[str] = None

    # Google Ads API
    google_ads_developer_token: Optional[str] = None
    google_ads_client_id: Optional[str] = None
    google_ads_client_secret: Optional[str] = None
    google_ads_refresh_token: Optional[str] = None
    google_ads_customer_id: Optional[str] = None

    # Cursor Agent SDK
    cursor_api_key: Optional[str] = None
    cursor_model: str = "composer-2.5"
    cursor_agent_cwd: Optional[str] = None

    # Token Settings
    token_initial_supply: float = 1000000.0
    token_decimal_places: int = 8
    token_issuance_rate: float = 0.1
    token_burn_rate: float = 0.05

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Overmind
    overmind_project_id: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()