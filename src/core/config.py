import os
from enum import Enum
from pathlib import Path
from typing import List

from pydantic import AnyHttpUrl, BaseModel, PostgresDsn
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent


# Commented for docker secrets
# def read_secret(env_var_name):
#     secret_name = env_var_name.lower()
#     secret_path = f'/run/secrets/{secret_name}'
#     try:
#         with open(secret_path) as f:
#             return f.read().strip()
#     except FileNotFoundError:
#         return os.getenv(env_var_name)


class AppEnvironment(str, Enum):
    PRODUCTION = "production"
    DEV = "development"
    TESTING = "testing"


class AuthJWT(BaseModel) :
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRATION_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRATION_DAYS: int = 30


class Config(BaseSettings):
    PROJECT_NAME: str | None = "Project Name"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl | str] = []
    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    DATABASE_URL: PostgresDsn = "db"
    # REDIS_URL: str = "redis://:@redis:6379"
    ENABLE_SENTRY: bool = False
    SENTRY_DSN: str | None = None
    FASTAPI_ENV: AppEnvironment = AppEnvironment.DEV

    APP_VERSION: str = "1"
    LOGGING_LEVEL: str = "INFO"
    API_V1_STR: str = "/api/v1"
    WS_PREFIX: str = "/ws"

    AUTH_JWT: AuthJWT = AuthJWT()

    def is_dev(self) -> bool:
        return self.FASTAPI_ENV == AppEnvironment.DEV

    def is_prod(self) -> bool:
        return self.FASTAPI_ENV == AppEnvironment.PRODUCTION


settings = Config(_env_file="infra/envs/.env", _env_file_encoding="utf-8")
