from __future__ import annotations

import logging

import sentry_sdk
from sentry_sdk import Hub

from src.core.config import settings

logger = logging.getLogger(__name__)


def init_sentry(*, for_fastapi: bool) -> None:
    if not settings.ENABLE_SENTRY:
        return

    if for_fastapi:
        dsn = settings.SENTRY_API_DSN or settings.SENTRY_DSN
    else:
        dsn = settings.SENTRY_DSN or settings.SENTRY_API_DSN

    if not dsn:
        return

    current_client = Hub.current.client
    current_dsn = str(getattr(current_client, "dsn", "")) if current_client else ""
    if current_dsn and current_dsn == dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        send_default_pii=for_fastapi,
        traces_sample_rate=0.1,
        environment=settings.FASTAPI_ENV.value,
        release=settings.APP_VERSION,
    )
    sentry_sdk.set_tag("service_name", settings.SERVICE_NAME)
