"""Deployment mode helpers."""

from __future__ import annotations

from typing import Any


def deployment_mode(config: dict[str, Any]) -> str:
    """Return normalized deployment mode.

    Supported modes are ``single`` and ``multi``.
    Defaults to ``single`` for backward compatibility.
    """

    mode = str(config.get("deployment", {}).get("mode", "single")).strip().lower()
    if mode not in {"single", "multi"}:
        return "single"
    return mode


def is_multi_mode(config: dict[str, Any]) -> bool:
    return deployment_mode(config) == "multi"