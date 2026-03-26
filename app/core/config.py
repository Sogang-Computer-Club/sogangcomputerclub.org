"""
설정 모듈 (Pydantic Settings).

모든 환경 변수를 한 곳에서 관리하여:
1. 타입 안전성 보장 (Pydantic 검증)
2. 기본값 제공 (로컬 개발용)
3. 프로덕션 설정 검증
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """환경 변수에서 로드되는 애플리케이션 설정."""

    # 데이터베이스 - 프로덕션에서는 반드시 환경 변수로 설정 필요
    database_url: str = Field(
        default="postgresql+asyncpg://memo_user:changeme@postgres:5432/memo_app",
        description="Database connection URL. MUST be set via environment variable in production.",
    )

    # 애플리케이션
    debug: bool = False
    log_level: str = "INFO"

    def validate_production_settings(self) -> None:
        """
        프로덕션 필수 설정 검증.

        debug=False일 때 기본값 사용 시 앱 시작을 차단하여
        보안 사고 방지 (기본 비밀번호로 프로덕션 운영 방지).
        """
        if not self.debug:
            if "changeme" in self.database_url.lower():
                raise ValueError(
                    "DATABASE_URL contains 'changeme'. Set a secure password in production."
                )

    # CORS - Allowed origins (comma-separated in env)
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """
    설정 인스턴스 반환 (캐시됨).

    lru_cache로 한 번만 로드하여:
    1. 환경 변수 파싱 비용 절약
    2. 앱 전체에서 동일한 설정 객체 사용 보장
    """
    settings = Settings()
    settings.validate_production_settings()
    return settings
