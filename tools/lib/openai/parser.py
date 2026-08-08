"""Utilities for parsing OpenAI protocol requests."""

from fastapi import Request

from lib.openai.chat.models import ChatCompletionRequest


def _parse_optional_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


async def parse_chat_completion(
    request: Request,
) -> ChatCompletionRequest:
    """Parse an OpenAI Chat Completions request."""

    body = await request.json()

    extra = dict(body)

    extra.pop("model", None)
    extra.pop("messages", None)
    extra.pop("stream", None)
    # Lifted to first-class fields; remove from passthrough dict.
    extra.pop("max_tokens", None)
    extra.pop("max_completion_tokens", None)

    return ChatCompletionRequest(
        model=body["model"],
        messages=body["messages"],
        stream=body.get("stream", False),
        max_tokens=_parse_optional_int(body.get("max_tokens")),
        max_completion_tokens=_parse_optional_int(body.get("max_completion_tokens")),
        extra=extra,
    )