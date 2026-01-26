from __future__ import annotations

import logging
import os
import time
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar

import sentry_sdk

from src.core.logging_ctx import job_context

logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, Histogram, start_http_server
except ImportError:  # pragma: no cover
    Counter = None
    Histogram = None
    start_http_server = None

_METRICS_STARTED_PORTS: set[int] = set()

if Counter and Histogram:
    JOBS_TOTAL = Counter(
        "jobs_total",
        "Total processed jobs",
        labelnames=("job_name", "status"),
    )
    JOB_DURATION_SECONDS = Histogram(
        "job_duration_seconds",
        "Job duration in seconds",
        labelnames=("job_name",),
    )
else:  # pragma: no cover
    JOBS_TOTAL = None
    JOB_DURATION_SECONDS = None

T = TypeVar("T", bound=Callable[..., Awaitable[Any]])


def start_metrics_http_server_from_env(env_var: str, *, default_port: int) -> int:
    value = os.getenv(env_var)
    if value is None or value == "":
        port = default_port
    else:
        try:
            port = int(value)
        except ValueError:
            logger.warning("Invalid %s=%r; using default_port=%s", env_var, value, default_port)
            port = default_port

    if port <= 0:
        return -1

    if not start_http_server:  # pragma: no cover
        logger.info("prometheus_client not installed; metrics disabled")
        return -1

    if port in _METRICS_STARTED_PORTS:
        return -1

    start_http_server(port)
    _METRICS_STARTED_PORTS.add(port)
    return port


def instrument_job(func: T) -> T:
    if getattr(func, "_instrumented", False):
        return func

    @wraps(func)
    async def wrapper(ctx: Any, *args: Any, **kwargs: Any) -> Any:
        job_name = getattr(func, "__name__", "job")
        job_id = None
        job_try = None
        if isinstance(ctx, dict):
            job_id = ctx.get("job_id")
            job_try = ctx.get("job_try")

        start = time.perf_counter()
        with job_context(job_name=job_name, job_id=str(job_id) if job_id else None, job_try=job_try):
            try:
                result = await func(ctx, *args, **kwargs)
            except Exception as exc:
                sentry_sdk.capture_exception(exc)
                if JOBS_TOTAL:
                    JOBS_TOTAL.labels(job_name=job_name, status="error").inc()
                raise
            else:
                if JOBS_TOTAL:
                    JOBS_TOTAL.labels(job_name=job_name, status="success").inc()
                return result
            finally:
                duration = time.perf_counter() - start
                if JOB_DURATION_SECONDS:
                    JOB_DURATION_SECONDS.labels(job_name=job_name).observe(duration)

    wrapper._instrumented = True  # type: ignore[attr-defined]
    return wrapper  # type: ignore[return-value]
