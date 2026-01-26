from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from src.core.logging_ctx import get_job_id
from src.core.trace import get_request_uuid, get_server_uuid

_RESERVED_RECORD_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "message",
    "module",
    "msecs",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "taskName",
    "thread",
    "threadName",
}


class JsonFormatter(logging.Formatter):
    def __init__(self, *, service_name: str | None = None) -> None:
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "PID": record.process,
        }

        service_name = getattr(record, "service_name", None) or self.service_name
        if service_name:
            data["service_name"] = service_name

        request_uuid = getattr(record, "uuid", None) or get_request_uuid()
        if request_uuid:
            data["uuid"] = request_uuid

        server_uuid = getattr(record, "uuid_server", None) or get_server_uuid()
        if server_uuid:
            data["uuid_server"] = server_uuid

        message = record.getMessage()
        if message:
            data["message"] = message

        for key, value in record.__dict__.items():
            if key in _RESERVED_RECORD_ATTRS or key.startswith("_"):
                continue
            if key in data:
                continue
            if value is None:
                continue
            data[key] = value

        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)

        return json.dumps(data, ensure_ascii=False, default=str)


class JobJsonFormatter(logging.Formatter):
    def __init__(self, *, service_name: str | None = None) -> None:
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        service_name = getattr(record, "service_name", None) or self.service_name
        job_id = getattr(record, "job_id", None) or get_job_id()

        payload: dict[str, Any] = {}
        record_payload = getattr(record, "payload", None)
        if isinstance(record_payload, Mapping):
            payload.update(record_payload)
        elif record_payload is not None:
            payload["data"] = record_payload

        message = record.getMessage()
        if message:
            payload.setdefault("message", message)

        for key, value in record.__dict__.items():
            if key in _RESERVED_RECORD_ATTRS or key.startswith("_"):
                continue
            if key in {"service_name", "job_id", "payload"}:
                continue
            if value is None:
                continue
            payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        data: dict[str, Any] = {
            "service_name": service_name,
            "job_id": job_id,
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "PID": record.process,
            "payload": payload,
            "level": record.levelname,
        }
        return json.dumps(data, ensure_ascii=False, default=str)


def _configure_root_logging(*, handler: logging.Handler, logging_level: str, disable_uvicorn_access_log: bool) -> None:
    level = getattr(logging, logging_level.upper(), logging.INFO)
    if not isinstance(level, int):
        level = logging.INFO

    logging.basicConfig(level=level, handlers=[handler], force=True)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True

    if disable_uvicorn_access_log:
        logging.getLogger("uvicorn.access").disabled = True


def configure_logging(
    *,
    logging_level: str = "INFO",
    service_name: str | None = None,
    disable_uvicorn_access_log: bool = True,
) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter(service_name=service_name))
    _configure_root_logging(
        handler=handler,
        logging_level=logging_level,
        disable_uvicorn_access_log=disable_uvicorn_access_log,
    )


def configure_job_logging(
    *,
    logging_level: str = "INFO",
    service_name: str | None = None,
    disable_uvicorn_access_log: bool = True,
) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JobJsonFormatter(service_name=service_name))
    _configure_root_logging(
        handler=handler,
        logging_level=logging_level,
        disable_uvicorn_access_log=disable_uvicorn_access_log,
    )
