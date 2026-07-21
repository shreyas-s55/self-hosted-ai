"""Gateway authentication middleware."""

import os

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


PUBLIC_PATHS = {
    "/",
    "/health",
}


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Simple bearer-token authentication middleware."""

    def __init__(self, app):
        super().__init__(app)

        self.enabled = (
            os.getenv("GATEWAY_AUTH_ENABLED", "false").lower() == "true"
        )

        self.api_key = os.getenv("GATEWAY_API_KEY")

    async def dispatch(self, request: Request, call_next):
        # Authentication disabled
        if not self.enabled:
            return await call_next(request)

        path = request.url.path

        # Public endpoints
        if path in PUBLIC_PATHS:
            return await call_next(request)

        # Protect only OpenAI API routes
        if not path.startswith("/v1"):
            return await call_next(request)

        auth = request.headers.get("Authorization")

        if not auth:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "message": "Missing API key.",
                        "type": "authentication_error",
                        "code": "missing_api_key",
                    }
                },
            )

        expected = f"Bearer {self.api_key}"

        if auth != expected:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "message": "Invalid API key.",
                        "type": "authentication_error",
                        "code": "invalid_api_key",
                    }
                },
            )

        return await call_next(request)