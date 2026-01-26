from __future__ import annotations

from contextvars import ContextVar
from uuid import UUID, uuid4

REQUEST_UUID_HEADER = "X-Request-UUID"
SERVER_UUID_HEADER = "X-Server-UUID"

request_uuid_ctx: ContextVar[str | None] = ContextVar("request_uuid", default=None)
server_uuid_ctx: ContextVar[str | None] = ContextVar("server_uuid", default=None)


def parse_uuid(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return str(UUID(value))
    except ValueError:
        return None


def new_uuid() -> str:
    return str(uuid4())


def get_request_uuid() -> str | None:
    return request_uuid_ctx.get()


def get_server_uuid() -> str | None:
    return server_uuid_ctx.get()
