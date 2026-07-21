"""Request ID middleware."""

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a request ID to every request."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER)

        if not request_id:
            request_id = str(uuid4())

        request.state.request_id = request_id

        response = await call_next(request)

        response.headers[REQUEST_ID_HEADER] = request_id

        return response