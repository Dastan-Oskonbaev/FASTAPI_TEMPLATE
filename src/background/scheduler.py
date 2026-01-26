import logging

from src.core.config import settings
from src.core.logging_config import configure_job_logging
from src.core.logging_ctx import JobContextFilter
from src.core.metrics.worker_metrics import instrument_job, start_metrics_http_server_from_env
from src.core.redis_lifecycle import redis_settings
from src.core.sentry import init_sentry


async def startup(ctx):
    init_sentry(for_fastapi=False)
    configure_job_logging(logging_level=settings.LOGGING_LEVEL, service_name=settings.SERVICE_NAME)
    for handler in logging.getLogger().handlers:
        handler.addFilter(JobContextFilter())

    port = start_metrics_http_server_from_env("SCHEDULER_METRICS_PORT", default_port=settings.SCHEDULER_METRICS_PORT)
    logging.getLogger(__name__).info("Scheduler metrics exporter on port %s", port if port != -1 else "already started")


async def shutdown(ctx):
    logging.getLogger(__name__).info("ARQ worker shutdown")


class SchedulerWorkerSettings:
    queue_name = "scheduler"
    functions = []
    cron_jobs = []
    redis_settings = redis_settings
    on_startup = startup
    on_shutdown = shutdown


SchedulerWorkerSettings.functions = [instrument_job(func) for func in SchedulerWorkerSettings.functions]
