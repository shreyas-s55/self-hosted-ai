"""Load gateway deployments from environment variables."""

from __future__ import annotations

import json
import os

from lib.gateway.deployment.model import GatewayDeployment


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
            default=is_default,
        )

    return deployments