"""OpenAI Chat Completions protocol models."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class ChatCompletionRequest:
    """Parsed OpenAI Chat Completions request."""

    model: str
    messages: list[dict[str, Any]]
    stream: bool = False

    # Preserve the original request payload so it can be forwarded
    # after validation or transformation.
    body: dict[str, Any] = field(default_factory=dict)