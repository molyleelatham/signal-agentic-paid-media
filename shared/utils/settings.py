"""
Application settings using pydantic-settings.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
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
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/signal"
    database_sync_url: str = "postgresql://user:password@localhost:5432/signal"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # External APIs
    tavily_api_key: Optional[str] = None
    thrad_api_key: Optional[str] = None
    overmind_api_key: Optional[str] = None
    
    # Platform APIs
    meta_api_key: Optional[str] = None
    meta_api_secret: Optional[str] = None
    google_ads_developer_token: Optional[str] = None
    google_ads_client_id: Optional[str] = None
    google_ads_client_secret: Optional[str] = None
    
    # JWT
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440
    
    # Token Settings
    token_initial_supply: float = 1000000.0
    token_decimal_places: int = 8
    token_issuance_rate: float = 0.1
    token_burn_rate: float = 0.05
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    prometheus_port: int = 9090
    
    # Modal (GPU Inference)
    modal_token: Optional[str] = None
    
    # Overmind
    overmind_project_id: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()