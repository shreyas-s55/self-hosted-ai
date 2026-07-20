"""AI Gateway service definition."""

from typing import Any

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
        model_name = config["model"]["name"]
        host_port = config.get("gateway", {}).get("port", _CONTAINER_PORT)

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
            "depends_on": {
                engine: {"condition": "service_healthy"},
            },
            "environment": {
                "GATEWAY_RUNTIME_URL": f"http://{engine}:{port}/v1",
                "GATEWAY_RUNTIME": engine,
                "GATEWAY_MODEL_NAME": model_name,
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
