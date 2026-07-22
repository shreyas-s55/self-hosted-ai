"""Gateway deployment registry."""

from __future__ import annotations

from lib.gateway.deployment.loader import load_deployments
from lib.gateway.deployment.model import GatewayDeployment


class GatewayDeploymentRegistry:
    """Runtime deployment registry."""

    def __init__(self, deployments: dict[str, GatewayDeployment]) -> None:
        self._deployments = deployments

    @classmethod
    def from_environment(cls) -> "GatewayDeploymentRegistry":
        return cls(load_deployments())

    def resolve(self, alias: str) -> GatewayDeployment:
        try:
            return self._deployments[alias]
        except KeyError:
            raise ValueError(f"Unknown deployment alias: {alias}") from None

    def aliases(self) -> tuple[str, ...]:
        return tuple(self._deployments.keys())

    def default(self) -> GatewayDeployment:
        if not self._deployments:
            raise ValueError("No deployments configured.")

        return next(iter(self._deployments.values()))