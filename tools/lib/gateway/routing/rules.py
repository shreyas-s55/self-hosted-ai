"""Rule-based request classification for deployment routing."""

from __future__ import annotations

from typing import Any

_CODER_KEYWORDS = (
    "python",
    "java",
    "javascript",
    "c++",
    "terraform",
    "ansible",
    "kubernetes",
    "docker",
    "sql",
    "regex",
    "stack trace",
    "exception",
    "traceback",
    "compile",
    "code",
    "bug",
    "debug",
)

_REASONING_KEYWORDS = (
    "prove",
    "proof",
    "reason",
    "logic",
    "mathematically",
    "derive",
    "theorem",
    "equation",
)


def classify(messages: list[dict[str, Any]]) -> str:
    """Classify a chat request into deployment alias candidates.

    Returns one of ``coder``, ``reasoning``, or ``chat``.
    """

    haystack = _flatten_messages(messages)

    if _contains_any(haystack, _CODER_KEYWORDS):
        return "coder"

    if _contains_any(haystack, _REASONING_KEYWORDS):
        return "reasoning"

    return "chat"


def _contains_any(haystack: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in haystack for keyword in keywords)


def _flatten_messages(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []

    for message in messages:
        content = message.get("content")

        if isinstance(content, str):
            parts.append(content)
            continue

        # OpenAI content can be structured as a list of content parts.
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        parts.append(text)

    return "\n".join(parts).lower()