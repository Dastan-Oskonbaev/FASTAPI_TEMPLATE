from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import List

from pydantic import AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR.parent / ".env"


class AppEnvironment(str, Enum):
    PRODUCTION = "production"
    DEV = "development"
    TESTING = "testing"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
    )

    PROJECT_NAME: str | None = "Project Name"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl | str] = []
    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    SECRET_KEY: str = "secret_api_key"

    DATABASE_URL: PostgresDsn
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    ENABLE_SENTRY: bool = False
    SENTRY_DSN: str | None = None
    SENTRY_API_DSN: str | None = None
    FASTAPI_ENV: AppEnvironment = AppEnvironment.DEV

    APP_VERSION: str = "1"
    LOGGING_LEVEL: str = "INFO"
    SERVICE_NAME: str = "WEB"
    API_V1_STR: str = "/api/v1"
    WS_PREFIX: str = "/ws"

    ENABLE_REQUEST_UUID: bool = True
    ENABLE_SERVER_UUID: bool = True
    REQUEST_UUID_HEADER: str = "X-Request-UUID"
    SERVER_UUID_HEADER: str = "X-Server-UUID"
    UUID_SERVER: str | None = None
    GENERATE_UUID_SERVER: bool = True

    LOG_REQUEST_BODY: bool = True
    LOG_REQUEST_BODY_MAX_BYTES: int = 10_000

    WORKER_METRICS_PORT: int = 9100
    SCHEDULER_METRICS_PORT: int = 9101

    def is_dev(self) -> bool:
        return self.FASTAPI_ENV == AppEnvironment.DEV

    def is_prod(self) -> bool:
        return self.FASTAPI_ENV == AppEnvironment.PRODUCTION


settings = Settings()
