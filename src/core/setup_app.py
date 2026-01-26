from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.middlewares import RequestLoggingMiddleware
from src.core.redis_lifecycle import close_redis_pool, init_redis_pool
from src.core.sentry import init_sentry


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis_pool(app)
    yield
    await close_redis_pool(app)


def create_app() -> FastAPI:
    init_sentry(for_fastapi=True)
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.APP_VERSION,
        docs_url=None if settings.is_prod() else "/docs",
        redoc_url=None if settings.is_prod() else "/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
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
    app.add_middleware(
        RequestLoggingMiddleware,
        service_name=settings.SERVICE_NAME,
        enable_request_uuid=settings.ENABLE_REQUEST_UUID,
        enable_server_uuid=settings.ENABLE_SERVER_UUID,
        request_uuid_header=settings.REQUEST_UUID_HEADER,
        server_uuid_header=settings.SERVER_UUID_HEADER,
        server_uuid=settings.UUID_SERVER,
        generate_server_uuid=settings.GENERATE_UUID_SERVER,
        log_request_body=settings.LOG_REQUEST_BODY,
        log_request_body_max_bytes=settings.LOG_REQUEST_BODY_MAX_BYTES,
    )
