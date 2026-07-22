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

    # Preserve additional OpenAI parameters
    extra: dict[str, Any] = field(default_factory=dict)

    def with_model(self, model: str) -> "ChatCompletionRequest":
        """Return a copy using a different model."""
        return replace(self, model=model)

    def to_dict(self) -> dict[str, Any]:
        """Serialize back to an OpenAI request."""

        payload = {
            "model": self.model,
            "messages": self.messages,
            **self.extra,
        }

        if self.stream:
            payload["stream"] = True

        return payload