"""
Configuration module using Pydantic Settings.
Centralizes all environment variable handling.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql+asyncpg://memo_user:phoenix@postgres:5432/memo_app"
    
    # Redis
    redis_url: str = "redis://redis:6379"
    
    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"
    
    # Application
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra env vars


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
