"""Gateway request routing service.

Routing is deployment-driven and intentionally isolated from FastAPI
route handlers and runtime proxy implementation details.
"""

from __future__ import annotations

from lib.gateway.deployment import (
    GatewayDeployment,
    GatewayDeploymentRegistry,
)
from lib.gateway.logging import get_logger
from lib.gateway.routing.rules import classify
from lib.openai.chat.models import ChatCompletionRequest

_logger = get_logger()


class RoutingService:
    """Resolve incoming requests to gateway deployments."""

    def __init__(self, deployments: GatewayDeploymentRegistry) -> None:
        self._deployments = deployments

    def route(self, request: ChatCompletionRequest) -> GatewayDeployment:
        """Route a request to a deployment.

        - ``model='auto'``  — classifies via keyword rules then resolves.
        - any other value   — resolved directly as a deployment alias.
        """

        if request.model == "auto":
            candidate, matched_keyword = classify(request.messages)

            if candidate == "chat":
                deployment = self._deployments.default()
            else:
                try:
                    deployment = self._deployments.resolve(candidate)
                except ValueError:
                    # Preserve backward compatibility for single-deployment mode.
                    deployment = self._deployments.default()

            _logger.info(
                "routing.auto",
                extra={
                    "model": "auto",
                    "rule": candidate,
                    "matched_keyword": matched_keyword,
                    "deployment": deployment.alias,
                },
            )
            return deployment

        deployment = self._deployments.resolve(request.model)
        _logger.info(
            "routing.explicit",
            extra={
                "model": request.model,
                "deployment": deployment.alias,
            },
        )
        return deployment
