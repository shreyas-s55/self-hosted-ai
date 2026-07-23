"""Gateway request routing service.

Routing is deployment-driven and intentionally isolated from FastAPI
route handlers and runtime proxy implementation details.
"""

from __future__ import annotations

from lib.gateway.deployment import (
    GatewayDeployment,
    GatewayDeploymentRegistry,
)
from lib.openai.chat.models import ChatCompletionRequest


class RoutingService:
    """Resolve incoming requests to gateway deployments."""

    def __init__(self, deployments: GatewayDeploymentRegistry) -> None:
        self._deployments = deployments

    def route(self, request: ChatCompletionRequest) -> GatewayDeployment:
        """Route a request to a deployment.

        Phase 2 behavior:
        - ``model='auto'`` routes to the configured default deployment.
        - all other model aliases preserve exact resolution behavior.
        """

        if request.model == "auto":
            return self._deployments.default()

        return self._deployments.resolve(request.model)