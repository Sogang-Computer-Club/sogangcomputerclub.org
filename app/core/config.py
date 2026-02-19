"""
Configuration module using Pydantic Settings.
Centralizes all environment variable handling.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database - No default password for security
    database_url: str = Field(
        default="postgresql+asyncpg://memo_user:changeme@postgres:5432/memo_app",
        description="Database connection URL. MUST be set via environment variable in production."
    )

    # Redis
    redis_url: str = "redis://redis:6379"

    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"

    # AWS SQS (alternative to Kafka)
    sqs_queue_url: str | None = None
    aws_region: str = "ap-northeast-2"
    event_backend: str = Field(
        default="kafka",
        description="Event backend: 'kafka', 'sqs', or 'null'"
    )

    # Application
    debug: bool = False
    log_level: str = "INFO"

    # Security - JWT settings
    secret_key: str = Field(
        default="CHANGE_THIS_IN_PRODUCTION_USE_STRONG_SECRET_KEY",
        description="Secret key for JWT signing. MUST be set via environment variable."
    )
    access_token_expire_minutes: int = 30

    def validate_production_settings(self) -> None:
        """Validate that production-critical settings are properly configured."""
        if not self.debug:
            if self.secret_key == "CHANGE_THIS_IN_PRODUCTION_USE_STRONG_SECRET_KEY":
                raise ValueError(
                    "SECRET_KEY must be set to a secure value in production. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
                )
            if "changeme" in self.database_url.lower():
                raise ValueError(
                    "DATABASE_URL contains 'changeme'. Set a secure password in production."
                )

    # CORS - Allowed origins (comma-separated in env)
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.validate_production_settings()
    return settings
