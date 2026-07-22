"""Gateway application service.

Coordinates gateway operations between the HTTP routes and the runtime
proxy. Business logic should live here rather than inside FastAPI route
handlers.

Initially this service is a thin wrapper around :class:`RuntimeProxy`.
Future responsibilities include:

- Deployment resolution
- Model validation
- Request transformation
- Runtime selection
"""

from fastapi import Request
from fastapi.responses import Response, StreamingResponse

from lib.gateway.proxy import RuntimeProxy


class GatewayService:
    """Application service for gateway operations."""

    def __init__(self, proxy: RuntimeProxy) -> None:
        self._proxy = proxy

    async def chat_completions(
        self,
        request: Request,
    ) -> Response | StreamingResponse:
        """Forward a chat completion request to the configured runtime."""
        return await self._proxy.forward(request, "/chat/completions")