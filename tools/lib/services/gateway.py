"""AI Gateway service definition."""

import json
from typing import Any

from lib.deployment import DeploymentResolver, is_multi_mode
from lib.services.base import BaseService

# Internal port the gateway container always listens on.
_CONTAINER_PORT = 9000


class GatewayService(BaseService):
    """Compose service definition for the AI Gateway.

    The gateway container is built from source at deploy time using the
    project root as the build context, so no pre-built image is required.

    Open WebUI points to the gateway (not directly to the runtime) when
    this service is enabled.
    """

    @property
    def name(self) -> str:
        return "gateway"

    def enabled(self, config: dict[str, Any]) -> bool:
        return config.get("gateway", {}).get("enabled", True)

    def build(self, config: dict[str, Any]) -> dict[str, Any]:
        runtime = config["runtime"]
        engine = runtime["engine"]
        port = runtime["port"]
        host_port = config.get("gateway", {}).get("port", _CONTAINER_PORT)

        resolver = DeploymentResolver(config)

        multi_mode = is_multi_mode(config)

        # Single mode: only the default deployment is deployed and exposed.
        # Multi mode: every deployment has its own runtime and is exposed.
        if multi_mode:
            aliases_to_expose = resolver.aliases()
        else:
            aliases_to_expose = (resolver.default().deployment.alias,)

        gateway_models = ",".join(aliases_to_expose)

        # Export deployment metadata so the gateway can resolve model aliases
        # at runtime without requiring config.yaml.
        gateway_deployments: dict[str, dict[str, str]] = {}
        depends_on: dict[str, dict[str, str]] = {}

        for alias in aliases_to_expose:
            deployment = resolver.resolve(alias)
            deployment_engine = deployment.deployment.runtime or engine

            runtime_service = deployment_engine

            if multi_mode:
                runtime_service = f"runtime-{alias}"

            gateway_deployments[alias] = {
                "repository": deployment.metadata.huggingface_repo,
                "runtime": deployment_engine,
                "runtime_url": f"http://{runtime_service}:{port}/v1",
                "runtime_service": runtime_service,
                "supports_tool_calling": str(
                    deployment.metadata.supports_tool_calling
                ).lower() == "true",
            }

            depends_on[runtime_service] = {"condition": "service_healthy"}

        default_deployment = resolver.default().deployment.alias

        healthcheck_script = (
            "import urllib.request; "
            f"urllib.request.urlopen('http://localhost:{_CONTAINER_PORT}/health')"
        )

        return {
            "build": {
                # Build context is the project root, one level above deploy/.
                "context": "../",
                "dockerfile": "deploy/gateway/Dockerfile",
            },
            "container_name": "gateway",
            "restart": "unless-stopped",
            "ports": [f"{host_port}:{_CONTAINER_PORT}"],
            "depends_on": depends_on,
            "environment": {
                "GATEWAY_RUNTIME_URL": gateway_deployments[default_deployment]["runtime_url"],
                "GATEWAY_RUNTIME": engine,
                "GATEWAY_MODELS": gateway_models,
                "GATEWAY_DEFAULT_DEPLOYMENT": default_deployment,
                "GATEWAY_DEPLOYMENTS": json.dumps(gateway_deployments),

                # Authentication
                "GATEWAY_AUTH_ENABLED": str(
                    config["gateway"]["authentication"]["enabled"]
                ).lower(),
                "GATEWAY_API_KEY": config["gateway"]["authentication"]["api_key"],
            },
            "expose": [str(_CONTAINER_PORT)],
            "healthcheck": {
                "test": ["CMD", "python3", "-c", healthcheck_script],
                "interval": "10s",
                "timeout": "5s",
                "retries": 30,
                "start_period": "30s",
            },
            "networks": ["ai-network"],
        }