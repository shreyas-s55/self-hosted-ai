"""Rule-based request classification for deployment routing."""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Keyword sets
# ---------------------------------------------------------------------------
# Keep keywords lowercase; matching is performed on a lowercased haystack
# using word-boundary guards so short terms like "api" do not match inside
# unrelated words (e.g. "capital", "interest").
#
# Deliberately excludes common English words that overlap with technical
# vocabulary ("class", "function", "method", "library", "rest", "test",
# "thread", "branch") to avoid false positives in conversational prompts.

_CODER_KEYWORDS: tuple[str, ...] = (
    # Languages
    "python",
    "javascript",
    "typescript",
    "java",
    "c++",
    "c#",
    "golang",
    "rust",
    "ruby",
    "swift",
    "kotlin",
    "scala",
    "php",
    "bash",
    "shell",
    "powershell",
    # Frameworks / libraries
    "fastapi",
    "flask",
    "django",
    "express",
    "react",
    "vue",
    "angular",
    "spring",
    "rails",
    "nextjs",
    # Web / API
    "endpoint",
    "api",
    "graphql",
    "webhook",
    "http",
    "middleware",
    # Cloud / infrastructure
    "aws",
    "s3",
    "lambda",
    "ec2",
    "cloudformation",
    "terraform",
    "ansible",
    "kubernetes",
    "helm",
    "kubectl",
    "docker",
    "dockerfile",
    "container",
    "ci/cd",
    "github actions",
    "pipeline",
    # Databases
    "sql",
    "query",
    "schema",
    "migration",
    "database",
    "postgres",
    "mysql",
    "sqlite",
    "mongodb",
    "redis",
    "orm",
    # Code constructs / patterns
    "async",
    "await",
    "coroutine",
    "recursion",
    "algorithm",
    "data structure",
    "regex",
    # Tooling / workflow
    "npm",
    "pip",
    "cargo",
    "git",
    "commit",
    "pull request",
    "lint",
    "refactor",
    "pytest",
    "unittest",
    "unit test",
    "mock",
    # Debugging
    "code",
    "bug",
    "debug",
    "stack trace",
    "exception",
    "traceback",
    "compile",
    "syntax error",
    # Data formats
    "json",
    "yaml",
    "xml",
    "csv",
    "serialize",
    "deserialize",
    # Protocols / security
    "nginx",
    "reverse proxy",
    "ssl",
    "certificate",
    "oauth",
    "jwt",
)

_REASONING_KEYWORDS: tuple[str, ...] = (
    "prove",
    "proof",
    "reason",
    "logic",
    "mathematically",
    "derive",
    "theorem",
    "equation",
    "calculate",
    "probability",
    "hypothesis",
    "axiom",
    "lemma",
    "corollary",
    "infer",
    "deduce",
    "formal",
    "contradiction",
)


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------


def classify(messages: list[dict[str, Any]]) -> tuple[str, str | None]:
    """Classify a chat request into a deployment alias candidate.

    Returns ``(alias, matched_keyword)`` where *alias* is one of
    ``"coder"``, ``"reasoning"``, or ``"chat"``, and *matched_keyword* is
    the first keyword that triggered the decision (``None`` for the
    ``"chat"`` fallback).
    """

    haystack = _flatten_messages(messages)

    match = _find_match(haystack, _CODER_KEYWORDS)
    if match:
        return "coder", match

    match = _find_match(haystack, _REASONING_KEYWORDS)
    if match:
        return "reasoning", match

    return "chat", None


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


# Compiled regex cache — built once per keyword on first use.
_PATTERN_CACHE: dict[str, re.Pattern[str]] = {}


def _word_pattern(keyword: str) -> re.Pattern[str]:
    if keyword not in _PATTERN_CACHE:
        # Negative lookbehind/lookahead for word chars rather than \b so that
        # keywords containing non-word characters ("c++", "ci/cd") work safely.
        _PATTERN_CACHE[keyword] = re.compile(
            r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
        )
    return _PATTERN_CACHE[keyword]


def _find_match(haystack: str, keywords: tuple[str, ...]) -> str | None:
    """Return the first keyword found at a word boundary in *haystack*."""
    return next(
        (kw for kw in keywords if _word_pattern(kw).search(haystack)),
        None,
    )


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
