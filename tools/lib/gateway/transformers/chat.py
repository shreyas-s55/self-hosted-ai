"""OpenAI Chat Completion request transformer."""

from __future__ import annotations

from lib.gateway.deployment import GatewayDeployment
from lib.openai.chat.models import ChatCompletionRequest


class ChatRequestTransformer:
    """Transforms OpenAI chat requests for the selected deployment."""

    def transform(
        self,
        request: ChatCompletionRequest,
        deployment: GatewayDeployment,
    ) -> ChatCompletionRequest:
        """Transform a request for the selected deployment."""
        transformed = request.with_model(deployment.repository)

        if deployment.supports_tool_calling:
            return transformed

        extra = dict(transformed.extra)

        # Open WebUI often sends tool-calling fields even for plain chat.
        # Remove them for deployments that were not started with tool support.
        extra.pop("tool_choice", None)
        extra.pop("tools", None)
        extra.pop("parallel_tool_calls", None)

        return ChatCompletionRequest(
            model=transformed.model,
            messages=transformed.messages,
            stream=transformed.stream,
            extra=extra,
        )