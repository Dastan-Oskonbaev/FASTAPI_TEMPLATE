from __future__ import annotations

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator

from src.core.trace import parse_uuid, request_uuid_ctx

job_name_ctx: ContextVar[str | None] = ContextVar("job_name", default=None)
job_id_ctx: ContextVar[str | None] = ContextVar("job_id", default=None)
job_try_ctx: ContextVar[int | None] = ContextVar("job_try", default=None)


@contextmanager
def job_context(
    *,
    job_name: str | None = None,
    job_id: str | None = None,
    job_try: int | None = None,
) -> Iterator[None]:
    normalized_job_id = parse_uuid(job_id) or job_id

    token_name = job_name_ctx.set(job_name)
    token_id = job_id_ctx.set(normalized_job_id)
    token_try = job_try_ctx.set(job_try)
    token_request_uuid = request_uuid_ctx.set(normalized_job_id)
    try:
        yield
    finally:
        job_name_ctx.reset(token_name)
        job_id_ctx.reset(token_id)
        job_try_ctx.reset(token_try)
        request_uuid_ctx.reset(token_request_uuid)


class JobContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        job_name = job_name_ctx.get()
        if job_name and not hasattr(record, "job_name"):
            record.job_name = job_name

        job_id = job_id_ctx.get()
        if job_id and not hasattr(record, "job_id"):
            record.job_id = job_id

        job_try = job_try_ctx.get()
        if job_try is not None and not hasattr(record, "job_try"):
            record.job_try = job_try

        return True


def get_job_id() -> str | None:
    return job_id_ctx.get()
