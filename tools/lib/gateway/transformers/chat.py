"""OpenAI Chat Completion request transformer."""

from __future__ import annotations

from typing import Any

from lib.gateway.deployment import GatewayDeployment
from lib.gateway.tokenizer import ChatPromptTokenEstimator
from lib.openai.chat.models import ChatCompletionRequest
from lib.openai.errors import OpenAIError


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


def _parse_requested_max_tokens(extra: dict[str, Any]) -> int | None:
    raw_max_tokens = extra.get("max_tokens")

    if raw_max_tokens is None:
        return None

    try:
        return int(raw_max_tokens)
    except (TypeError, ValueError):
        return None


class ChatRequestTransformer:
    """Transforms OpenAI chat requests for the selected deployment."""

    def __init__(self) -> None:
        self._token_estimator = ChatPromptTokenEstimator()

    def _normalize_max_tokens(
        self,
        *,
        request: ChatCompletionRequest,
        deployment: GatewayDeployment,
        extra: dict[str, Any],
    ) -> dict[str, Any]:
        requested_max_tokens = _parse_requested_max_tokens(extra)

        if requested_max_tokens is None:
            return extra

        context_window = deployment.context_window

        if context_window is None:
            return _clamp_max_tokens(
                extra,
                max_completion_tokens=deployment.max_completion_tokens,
            )

        prompt_tokens = self._token_estimator.estimate(
            repository=deployment.repository,
            messages=request.messages,
            tools=extra.get("tools"),
        )
        available_completion_tokens = context_window - prompt_tokens

        if available_completion_tokens <= 0:
            raise OpenAIError(
                status_code=400,
                code="context_length_exceeded",
                message=(
                    f'This deployment supports a maximum context length of '
                    f'{context_window} tokens, but the prompt is estimated at '
                    f'{prompt_tokens} tokens, leaving no room for completion.'
                ),
            )

        if requested_max_tokens <= available_completion_tokens:
            return extra

        clamped = dict(extra)
        clamped["max_tokens"] = available_completion_tokens
        return clamped

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

        extra = self._normalize_max_tokens(
            request=transformed,
            deployment=deployment,
            extra=extra,
        )

        return ChatCompletionRequest(
            model=transformed.model,
            messages=transformed.messages,
            stream=transformed.stream,
            extra=extra,
        )