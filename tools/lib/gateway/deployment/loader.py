"""Load gateway deployments from environment variables."""

from __future__ import annotations

import json
import os
from typing import Any

from lib.gateway.deployment.model import GatewayDeployment


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None

    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None

    if parsed <= 0:
        return None

    return parsed


def load_deployments() -> dict[str, GatewayDeployment]:
    """Load deployment metadata exported by the compose generator."""

    raw = os.environ.get("GATEWAY_DEPLOYMENTS", "{}")

    payload = json.loads(raw)
    default_runtime_url = os.environ.get("GATEWAY_RUNTIME_URL", "")
    default_alias = os.environ.get("GATEWAY_DEFAULT_DEPLOYMENT", "")

    deployments: dict[str, GatewayDeployment] = {}

    for alias, metadata in payload.items():
        is_default = (
            alias == default_alias
            if default_alias
            else len(deployments) == 0
        )
        deployments[alias] = GatewayDeployment(
            alias=alias,
            repository=metadata["repository"],
            runtime=metadata["runtime"],
            runtime_url=metadata.get("runtime_url", default_runtime_url),
            supports_tool_calling=bool(metadata.get("supports_tool_calling", False)),
            max_completion_tokens=_optional_int(
                metadata.get("max_completion_tokens")
            ),
                context_window=_optional_int(
                    metadata.get("context_window")
                ),
            default=is_default,
        )

    return deployments