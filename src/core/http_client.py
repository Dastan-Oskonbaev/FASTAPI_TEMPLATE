from __future__ import annotations

from functools import partial
from typing import Any, Mapping

import httpx

from src.core.logging_ctx import get_job_id
from src.core.trace import REQUEST_UUID_HEADER, SERVER_UUID_HEADER, get_request_uuid, get_server_uuid


def inject_trace_headers(
    headers: Mapping[str, str] | None = None,
    *,
    request_uuid_header: str = REQUEST_UUID_HEADER,
    server_uuid_header: str = SERVER_UUID_HEADER,
) -> dict[str, str]:
    merged = dict(headers or {})

    request_uuid = get_request_uuid() or get_job_id()
    if request_uuid:
        merged[request_uuid_header] = request_uuid

    server_uuid = get_server_uuid()
    if server_uuid:
        merged[server_uuid_header] = server_uuid

    return merged


async def traced_request_hook(
    request: httpx.Request,
    *,
    request_uuid_header: str = REQUEST_UUID_HEADER,
    server_uuid_header: str = SERVER_UUID_HEADER,
) -> None:
    request_uuid = get_request_uuid() or get_job_id()
    if request_uuid and request_uuid_header not in request.headers:
        request.headers[request_uuid_header] = request_uuid

    server_uuid = get_server_uuid()
    if server_uuid and server_uuid_header not in request.headers:
        request.headers[server_uuid_header] = server_uuid


def create_traced_async_client(
    *,
    request_uuid_header: str = REQUEST_UUID_HEADER,
    server_uuid_header: str = SERVER_UUID_HEADER,
    **kwargs: Any,
) -> httpx.AsyncClient:
    event_hooks: dict[str, list[Any]] = dict(kwargs.pop("event_hooks", {}) or {})
    request_hooks = list(event_hooks.get("request", []))
    request_hooks.append(
        partial(
            traced_request_hook,
            request_uuid_header=request_uuid_header,
            server_uuid_header=server_uuid_header,
        )
    )
    event_hooks["request"] = request_hooks

    return httpx.AsyncClient(event_hooks=event_hooks, **kwargs)
