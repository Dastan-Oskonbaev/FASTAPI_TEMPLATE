from __future__ import annotations

import logging
from typing import Any

from starlette.datastructures import Headers, MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.core.trace import (
    REQUEST_UUID_HEADER,
    SERVER_UUID_HEADER,
    new_uuid,
    parse_uuid,
    request_uuid_ctx,
    server_uuid_ctx,
)


class RequestLoggingMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        service_name: str,
        enable_request_uuid: bool = True,
        enable_server_uuid: bool = True,
        request_uuid_header: str = REQUEST_UUID_HEADER,
        server_uuid_header: str = SERVER_UUID_HEADER,
        server_uuid: str | None = None,
        generate_server_uuid: bool = True,
        log_request_body: bool = True,
        log_request_body_max_bytes: int = 10_000,
    ) -> None:
        self.app = app
        self.logger = logging.getLogger("http.request")
        self.service_name = service_name
        self.enable_request_uuid = enable_request_uuid
        self.enable_server_uuid = enable_server_uuid
        self.request_uuid_header = request_uuid_header
        self.server_uuid_header = server_uuid_header
        self.log_request_body = log_request_body
        self.log_request_body_max_bytes = log_request_body_max_bytes

        if server_uuid is not None:
            self.server_uuid = parse_uuid(server_uuid)
        elif enable_server_uuid and generate_server_uuid:
            self.server_uuid = new_uuid()
        else:
            self.server_uuid = None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        body_bytes = await _receive_all_body(receive)
        receive_replay = _build_receive_replay(body_bytes, receive)

        request = Request(scope, receive=receive_replay)
        headers = Headers(scope=scope)

        request_uuid = self._resolve_request_uuid(headers.get(self.request_uuid_header))
        server_uuid = self._resolve_server_uuid(headers.get(self.server_uuid_header))

        request_uuid_token = request_uuid_ctx.set(request_uuid)
        server_uuid_token = server_uuid_ctx.set(server_uuid)

        status_code: int | None = None

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                mutable_headers = MutableHeaders(scope=message)
                if request_uuid:
                    mutable_headers[self.request_uuid_header] = request_uuid
                if server_uuid:
                    mutable_headers[self.server_uuid_header] = server_uuid
            await send(message)

        try:
            await self.app(scope, receive_replay, send_wrapper)
        finally:
            self._log_request(request, body_bytes, status_code)
            request_uuid_ctx.reset(request_uuid_token)
            server_uuid_ctx.reset(server_uuid_token)

    def _resolve_request_uuid(self, incoming: str | None) -> str | None:
        if not self.enable_request_uuid:
            return None
        return parse_uuid(incoming) or new_uuid()

    def _resolve_server_uuid(self, incoming: str | None) -> str | None:
        if not self.enable_server_uuid:
            return None
        return parse_uuid(incoming) or self.server_uuid

    def _log_request(self, request: Request, body: bytes, status_code: int | None) -> None:
        payload: dict[str, Any] = {"url": str(request.url)}
        if self.log_request_body:
            payload["body"] = _safe_decode_body(body, max_bytes=self.log_request_body_max_bytes)

        extra: dict[str, Any] = {
            "request_method": request.method,
            "service_name": self.service_name,
            "payload": payload,
        }

        self.logger.log(_level_for_status(status_code), "", extra=extra)


def _level_for_status(status_code: int | None) -> int:
    if status_code is None:
        return logging.INFO
    if status_code >= 500:
        return logging.ERROR
    if status_code >= 400:
        return logging.WARNING
    return logging.INFO


async def _receive_all_body(receive: Receive) -> bytes:
    chunks: list[bytes] = []
    while True:
        message = await receive()
        if message["type"] == "http.disconnect":
            break
        if message["type"] != "http.request":
            continue
        chunks.append(message.get("body", b""))
        if not message.get("more_body", False):
            break
    return b"".join(chunks)


def _build_receive_replay(body: bytes, receive: Receive) -> Receive:
    sent = False

    async def replay() -> Message:
        nonlocal sent
        if not sent:
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        return await receive()

    return replay


def _safe_decode_body(body: bytes, *, max_bytes: int) -> str | None:
    if not body:
        return None
    truncated = body[:max_bytes]
    try:
        decoded = truncated.decode("utf-8")
    except UnicodeDecodeError:
        return f"<non-utf8 body length={len(body)} bytes>"
    if len(body) > max_bytes:
        return f"{decoded}<truncated length={len(body)} bytes>"
    return decoded
