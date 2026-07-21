"""Gateway request logging middleware."""

import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .logger import get_logger


logger = get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs every HTTP request."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        logger.info(
            "request",
            extra={
                "extra": {
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration_ms": duration_ms,
                    "client": request.client.host if request.client else None,
                }
            },
        )

        return response