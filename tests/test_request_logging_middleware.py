import json
import logging
from io import StringIO
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI

from src.core.logging_config import JsonFormatter
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
async def test_request_logging_generates_and_returns_uuids():
    stream, logger, prev_handlers, prev_propagate, prev_level = _capture_http_request_logs()
    try:
        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware, service_name="WEB")

        @app.post("/ping")
        async def ping():
            return {"ok": True}

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post("/ping", json={"a": 1})

        assert response.status_code == 200
        assert "X-Request-UUID" in response.headers
        assert "X-Server-UUID" in response.headers

        log_lines = [line for line in stream.getvalue().splitlines() if line.strip()]
        assert log_lines

        log_event = next(event for event in map(json.loads, log_lines) if event.get("request_method") == "POST")
        assert log_event["service_name"] == "WEB"
        assert log_event["uuid"] == response.headers["X-Request-UUID"]
        assert log_event["uuid_server"] == response.headers["X-Server-UUID"]
        assert log_event["payload"]["url"].endswith("/ping")
        assert "timestamp" in log_event
        assert "PID" in log_event
        assert log_event["level"] == "INFO"
    finally:
        _restore_logger(logger, prev_handlers, prev_propagate, prev_level)


@pytest.mark.anyio
async def test_request_logging_accepts_incoming_uuids():
    stream, logger, prev_handlers, prev_propagate, prev_level = _capture_http_request_logs()
    try:
        app = FastAPI()
        app.add_middleware(RequestLoggingMiddleware, service_name="WEB")

        @app.get("/ping")
        async def ping():
            return {"ok": True}

        incoming_uuid = str(uuid4())
        incoming_uuid_server = str(uuid4())
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/ping",
                headers={"X-Request-UUID": incoming_uuid, "X-Server-UUID": incoming_uuid_server},
            )

        assert response.status_code == 200
        assert response.headers["X-Request-UUID"] == incoming_uuid
        assert response.headers["X-Server-UUID"] == incoming_uuid_server

        log_lines = [line for line in stream.getvalue().splitlines() if line.strip()]
        assert log_lines

        log_event = next(event for event in map(json.loads, log_lines) if event.get("request_method") == "GET")
        assert log_event["uuid"] == incoming_uuid
        assert log_event["uuid_server"] == incoming_uuid_server
    finally:
        _restore_logger(logger, prev_handlers, prev_propagate, prev_level)


@pytest.mark.anyio
async def test_request_logging_optional_server_uuid():
    stream, logger, prev_handlers, prev_propagate, prev_level = _capture_http_request_logs()
    try:
        app = FastAPI()
        app.add_middleware(
            RequestLoggingMiddleware,
            service_name="WEB",
            enable_server_uuid=False,
        )

        @app.get("/ping")
        async def ping():
            return {"ok": True}

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/ping")

        assert response.status_code == 200
        assert "X-Server-UUID" not in response.headers

        log_lines = [line for line in stream.getvalue().splitlines() if line.strip()]
        assert log_lines

        log_event = next(event for event in map(json.loads, log_lines) if event.get("request_method") == "GET")
        assert "uuid_server" not in log_event
    finally:
        _restore_logger(logger, prev_handlers, prev_propagate, prev_level)
