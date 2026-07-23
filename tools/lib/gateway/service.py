"""Gateway application service.

Coordinates gateway operations between the HTTP routes and the runtime
proxy. Business logic lives here rather than inside FastAPI route
handlers.
"""

from __future__ import annotations

import json

from fastapi import Request
from fastapi.responses import Response, StreamingResponse

from lib.gateway.deployment import GatewayDeploymentRegistry
from lib.gateway.proxy import RuntimeProxy
from lib.openai.parser import parse_chat_completion
from lib.gateway.transformers import ChatRequestTransformer


class GatewayService:
    """Application service for gateway operations."""

    def __init__(
        self,
        proxy: RuntimeProxy,
        deployments: GatewayDeploymentRegistry,
    ) -> None:
        self._proxy = proxy
        self._deployments = deployments
        self._transformer = ChatRequestTransformer()

    async def chat_completions(
        self,
        request: Request,
    ) -> Response | StreamingResponse:
        """Process an OpenAI Chat Completions request."""

        # Parse the incoming request.
        chat = await parse_chat_completion(request)

        # Resolve the deployment alias.
        deployment = self._deployments.resolve(chat.model)

        # Transform the request to use the runtime model.
        transformed = self._transformer.transform(request=chat,deployment=deployment,)

        # Serialize back to JSON.
        payload = json.dumps(transformed.to_dict()).encode("utf-8")

        # Forward to the runtime.
        return await self._proxy.forward(
            request=request,
            path="/chat/completions",
            body=payload,
            stream=transformed.stream,
        )