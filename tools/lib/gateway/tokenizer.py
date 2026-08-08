"""Gateway tokenizer utilities.

Loads and caches Hugging Face tokenizers for routed deployments so the
gateway can estimate prompt tokens before forwarding requests upstream.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any

from transformers import AutoTokenizer


class ChatPromptTokenEstimator:
    """Estimate prompt token usage for OpenAI chat-completions payloads."""

    def estimate(
        self,
        *,
        repository: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> int:
        tokenizer = _load_tokenizer(repository)

        try:
            token_ids = tokenizer.apply_chat_template(
                messages,
                tools=tools,
                tokenize=True,
                add_generation_prompt=True,
            )
            return len(token_ids)
        except Exception:
            fallback_payload = json.dumps(
                {
                    "messages": messages,
                    "tools": tools or [],
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            encoded = tokenizer(
                fallback_payload,
                add_special_tokens=True,
                return_attention_mask=False,
                return_token_type_ids=False,
            )
            return len(encoded["input_ids"])


@lru_cache(maxsize=16)
def _load_tokenizer(repository: str):
    token = os.environ.get("HUGGING_FACE_HUB_TOKEN") or None

    try:
        return AutoTokenizer.from_pretrained(
            repository,
            token=token,
            use_fast=True,
        )
    except Exception:
        return AutoTokenizer.from_pretrained(
            repository,
            token=token,
            use_fast=False,
        )
