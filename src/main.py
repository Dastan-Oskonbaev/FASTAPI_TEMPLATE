from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.error_handlers import general_exception_handler, http_exception_handler, validation_exception_handler
from src.core.logging_config import configure_logging
from src.core.setup_app import create_app

configure_logging(logging_level=settings.LOGGING_LEVEL, service_name=settings.SERVICE_NAME)
app = create_app()


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck():
    return JSONResponse(content={"status": "ok"}, status_code=200)


app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
