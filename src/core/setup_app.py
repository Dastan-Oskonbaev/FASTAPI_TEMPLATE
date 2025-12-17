from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.redis_lifecycle import init_redis_pool, close_redis_pool
from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis_pool(app)
    yield
    await close_redis_pool(app)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.APP_VERSION,
        docs_url=None if settings.is_prod() else "/docs",
        redoc_url=None if settings.is_prod() else "/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )
    if settings.ENABLE_SENTRY and settings.SENTRY_API_DSN:
        import sentry_sdk

        sentry_sdk.init(
            dsn=settings.SENTRY_API_DSN,
            send_default_pii=True,
            traces_sample_rate=0.1,
        )
    setup_routers(app)
    setup_middlewares(app)

    return app


def setup_routers(app: FastAPI) -> None:
    pass


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=settings.CORS_HEADERS or ["*"],
    )
