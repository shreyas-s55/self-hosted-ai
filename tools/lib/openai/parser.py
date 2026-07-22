"""Utilities for parsing OpenAI protocol requests."""

from fastapi import Request

from lib.openai.chat.models import ChatCompletionRequest


async def parse_chat_completion(
    request: Request,
) -> ChatCompletionRequest:
    """Parse an OpenAI Chat Completions request."""

    body = await request.json()

    extra = dict(body)

    extra.pop("model", None)
    extra.pop("messages", None)
    extra.pop("stream", None)

    return ChatCompletionRequest(
        model=body["model"],
        messages=body["messages"],
        stream=body.get("stream", False),
        extra=extra,
    )