"""OpenAI Chat Completions protocol models."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any


@dataclass(slots=True, frozen=True)
class ChatCompletionRequest:
    """Parsed OpenAI Chat Completions request."""

    model: str
    messages: list[dict[str, Any]]
    stream: bool = False

    # max_tokens and max_completion_tokens are both supported at parse time.
    # The transformer resolves them to a single budget before forwarding.
    max_tokens: int | None = None
    max_completion_tokens: int | None = None

    # All remaining OpenAI parameters passthrough unchanged.
    extra: dict[str, Any] = field(default_factory=dict)

    def with_model(self, model: str) -> ChatCompletionRequest:
        """Return a copy using a different model."""
        return replace(self, model=model)

    def to_dict(self) -> dict[str, Any]:
        """Serialize back to an OpenAI request.

        Normalises to max_tokens for upstream; never emits max_completion_tokens
        so vLLM sees a consistent field.  max_completion_tokens takes precedence
        over max_tokens when both are set, mirroring the transformer's resolution.
        """
        payload = {
            "model": self.model,
            "messages": self.messages,
            **self.extra,
        }

        if self.stream:
            payload["stream"] = True

        # Strip both fields from any extra spillover, then emit one resolved value.
        payload.pop("max_tokens", None)
        payload.pop("max_completion_tokens", None)

        effective = (
            self.max_completion_tokens
            if self.max_completion_tokens is not None
            else self.max_tokens
        )
        if effective is not None:
            payload["max_tokens"] = effective

        return payload