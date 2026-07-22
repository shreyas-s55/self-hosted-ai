"""Gateway runtime deployment model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GatewayDeployment:
    """Deployment metadata available at gateway runtime."""

    alias: str
    repository: str
    runtime: str