"""OpenAI Chat Completion request transformer."""

from __future__ import annotations

from typing import Any

from lib.gateway.deployment import GatewayDeployment
from lib.openai.chat.models import ChatCompletionRequest


def _clamp_max_tokens(
    extra: dict[str, Any],
    *,
    max_completion_tokens: int | None,
) -> dict[str, Any]:
    if max_completion_tokens is None:
        return extra

    raw_max_tokens = extra.get("max_tokens")

    if raw_max_tokens is None:
        return extra

    try:
        requested = int(raw_max_tokens)
    except (TypeError, ValueError):
        return extra

    if requested <= max_completion_tokens:
        return extra

    clamped = dict(extra)
    clamped["max_tokens"] = max_completion_tokens
    return clamped


class ChatRequestTransformer:
    """Transforms OpenAI chat requests for the selected deployment."""

    def transform(
        self,
        request: ChatCompletionRequest,
        deployment: GatewayDeployment,
    ) -> ChatCompletionRequest:
        """Transform a request for the selected deployment."""
        transformed = request.with_model(deployment.repository)
        extra = _clamp_max_tokens(
            dict(transformed.extra),
            max_completion_tokens=deployment.max_completion_tokens,
        )

        if deployment.supports_tool_calling:
            return ChatCompletionRequest(
                model=transformed.model,
                messages=transformed.messages,
                stream=transformed.stream,
                extra=extra,
            )

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