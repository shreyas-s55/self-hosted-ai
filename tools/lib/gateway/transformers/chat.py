"""OpenAI Chat Completion request transformer."""

from __future__ import annotations

from typing import Any

from lib.gateway.deployment import GatewayDeployment
from lib.gateway.tokenizer import ChatPromptTokenEstimator
from lib.openai.chat.models import ChatCompletionRequest
from lib.openai.errors import OpenAIError

# Reserve a small safety margin for tokenizer/runtime differences.
_COMPLETION_SAFETY_MARGIN = 32


def _resolve_requested_completion_tokens(request: ChatCompletionRequest) -> int | None:
    """Return the client-requested completion budget from whichever field was sent.

    max_completion_tokens takes precedence (newer OpenAI API field).
    Falls back to max_tokens for older clients.
    """
    if request.max_completion_tokens is not None:
        return request.max_completion_tokens
    return request.max_tokens


class ChatRequestTransformer:
    """Transforms OpenAI chat requests for the selected deployment."""

    def __init__(self) -> None:
        self._token_estimator = ChatPromptTokenEstimator()

    def _compute_clamped_max_tokens(
        self,
        *,
        request: ChatCompletionRequest,
        deployment: GatewayDeployment,
        extra: dict[str, Any],
    ) -> int | None:
        """Return the clamped completion budget, or None to leave it unset."""
        requested = _resolve_requested_completion_tokens(request)

        if requested is None:
            return None

        context_window = deployment.context_window

        if context_window is None:
            # No context-window metadata: fall back to the hard deployment ceiling.
            ceiling = deployment.max_completion_tokens
            if ceiling is None or requested <= ceiling:
                return requested
            return ceiling

        prompt_tokens = self._token_estimator.estimate(
            repository=deployment.repository,
            messages=request.messages,
            tools=extra.get("tools"),
        )
        available = context_window - prompt_tokens - _COMPLETION_SAFETY_MARGIN

        if available <= 0:
            raise OpenAIError(
                status_code=400,
                code="context_length_exceeded",
                message=(
                    f"This deployment supports a maximum context length of "
                    f"{context_window} tokens, but the prompt is estimated at "
                    f"{prompt_tokens} tokens, leaving no room for completion."
                ),
            )

        return min(requested, available)

    def transform(
        self,
        request: ChatCompletionRequest,
        deployment: GatewayDeployment,
    ) -> ChatCompletionRequest:
        """Transform a request for the selected deployment."""
        transformed = request.with_model(deployment.repository)
        extra = dict(transformed.extra)

        if not deployment.supports_tool_calling:
            # Open WebUI often sends tool-calling fields even for plain chat.
            # Remove them for deployments that were not started with tool support.
            extra.pop("tool_choice", None)
            extra.pop("tools", None)
            extra.pop("parallel_tool_calls", None)

        clamped = self._compute_clamped_max_tokens(
            request=transformed,
            deployment=deployment,
            extra=extra,
        )

        return ChatCompletionRequest(
            model=transformed.model,
            messages=transformed.messages,
            stream=transformed.stream,
            max_tokens=clamped,
            # max_completion_tokens is always None on outbound; normalised to max_tokens above.
            max_completion_tokens=None,
            extra=extra,
        )