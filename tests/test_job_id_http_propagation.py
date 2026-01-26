import json
import logging
from io import StringIO
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI

from src.core.http_client import create_traced_async_client
from src.core.logging_config import JsonFormatter
from src.core.logging_ctx import job_context
from src.core.middlewares.request_logging import RequestLoggingMiddleware


def _capture_http_request_logs() -> tuple[StringIO, logging.Logger, list[logging.Handler], bool, int]:
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter(service_name="WEB"))

    logger = logging.getLogger("http.request")
    previous_handlers = list(logger.handlers)
    previous_propagate = logger.propagate
    previous_level = logger.level

    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    return stream, logger, previous_handlers, previous_propagate, previous_level


def _restore_logger(
    logger: logging.Logger, previous_handlers: list[logging.Handler], previous_propagate: bool, previous_level: int
) -> None:
    logger.handlers.clear()
    for handler in previous_handlers:
        logger.addHandler(handler)
    logger.propagate = previous_propagate
    logger.setLevel(previous_level)


@pytest.mark.anyio
async def test_job_id_propagates_as_request_uuid_header():
    stream, logger, prev_handlers, prev_propagate, prev_level = _capture_http_request_logs()
    try:
        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware, service_name="WEB")

        @app.get("/ping")
        async def ping():
            return {"ok": True}

        job_id = str(uuid4())
        transport = httpx.ASGITransport(app=app)

        with job_context(job_id=job_id):
            async with create_traced_async_client(transport=transport, base_url="http://testserver") as client:
                response = await client.get("/ping")

        assert response.status_code == 200
        assert response.headers["X-Request-UUID"] == job_id

        log_lines = [line for line in stream.getvalue().splitlines() if line.strip()]
        assert log_lines

        log_event = next(event for event in map(json.loads, log_lines) if event.get("request_method") == "GET")
        assert log_event["uuid"] == job_id
    finally:
        _restore_logger(logger, prev_handlers, prev_propagate, prev_level)

