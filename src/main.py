import logging

import sentry_sdk
from fastapi import Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.core.config import settings
from src.core.error_handlers import general_exception_handler, http_exception_handler, validation_exception_handler
from src.core.setup_app import create_app

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.DEBUG
)
app = create_app()


if bool(settings.ENABLE_SENTRY) and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,
    )


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck():
    return JSONResponse(content={"status": "ok"}, status_code=200)


app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)