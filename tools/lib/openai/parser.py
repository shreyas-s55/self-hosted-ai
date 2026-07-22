"""Utilities for parsing OpenAI protocol requests."""

from fastapi import Request

from lib.openai.chat.models import ChatCompletionRequest


async def parse_chat_completion(
    request: Request,
) -> ChatCompletionRequest:
    """Parse an OpenAI Chat Completions request."""

    body = await request.json()

    return ChatCompletionRequest(
        model=body["model"],
        messages=body["messages"],
        stream=body.get("stream", False),
        body=body,
    )