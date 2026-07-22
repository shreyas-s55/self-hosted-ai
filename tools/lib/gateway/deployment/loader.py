"""Load gateway deployments from environment variables."""

from __future__ import annotations

import json
import os

from lib.gateway.deployment.model import GatewayDeployment


def load_deployments() -> dict[str, GatewayDeployment]:
    """Load deployment metadata exported by the compose generator."""

    raw = os.environ.get("GATEWAY_DEPLOYMENTS", "{}")

    payload = json.loads(raw)

    deployments: dict[str, GatewayDeployment] = {}

    for alias, metadata in payload.items():
        deployments[alias] = GatewayDeployment(
            alias=alias,
            repository=metadata["repository"],
            runtime=metadata["runtime"],
        )

    return deployments