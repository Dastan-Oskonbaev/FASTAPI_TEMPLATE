import json
import logging

from src.core.logging_config import JobJsonFormatter
from src.core.logging_ctx import job_context


def test_job_json_formatter_shape():
    formatter = JobJsonFormatter(service_name="WORKER")
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.payload = {"foo": "bar"}

    with job_context(job_id="job-1"):
        data = json.loads(formatter.format(record))

    assert set(data.keys()) == {"service_name", "job_id", "timestamp", "PID", "payload", "level"}
    assert data["service_name"] == "WORKER"
    assert data["job_id"] == "job-1"
    assert data["level"] == "INFO"
    assert data["payload"] == {"foo": "bar", "message": "hello"}
