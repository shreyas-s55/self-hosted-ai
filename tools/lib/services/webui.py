"""Open WebUI service definition."""

from typing import Any

from lib.deployment import DeploymentResolver, is_multi_mode
from lib.services.base import BaseService

_GATEWAY_CONTAINER_PORT = 9000


class OpenWebUIService(BaseService):
    """Compose service definition for Open WebUI.

    When the gateway is enabled (default), Open WebUI communicates with
    the gateway instead of directly with the inference runtime.  This
    keeps the runtime off the direct request path and routes all API
    traffic through the gateway.

    When the gateway is disabled, Open WebUI falls back to talking
    directly to the runtime, preserving backward compatibility.
    """

    @property
    def name(self) -> str:
        return "open-webui"

    def enabled(self, config: dict[str, Any]) -> bool:
        return config.get("ui", {}).get("enabled", True)

    def build(self, config: dict[str, Any]) -> dict[str, Any]:
        gateway_enabled = config.get("gateway", {}).get("enabled", True)

        if gateway_enabled:
            gateway_port = config.get("gateway", {}).get("port", _GATEWAY_CONTAINER_PORT)
            api_base_url = f"http://gateway:{_GATEWAY_CONTAINER_PORT}/v1"
            depends_on = {"gateway": {"condition": "service_healthy"}}
        else:
            engine = config["runtime"]["engine"]
            port = config["runtime"]["port"]

            if is_multi_mode(config):
                resolver = DeploymentResolver(config)
                default_alias = resolver.default().deployment.alias
                runtime_service = f"runtime-{default_alias}"
            else:
                runtime_service = engine

            api_base_url = f"http://{runtime_service}:{port}/v1"
            depends_on = {runtime_service: {"condition": "service_healthy"}}

        return {
            "image": "ghcr.io/open-webui/open-webui:main",
            "container_name": "open-webui",
            "restart": "unless-stopped",
            "depends_on": depends_on,
            "expose": ["8080"],
            "environment": {
                "TZ": "UTC",
                "ENABLE_OLLAMA_API": "false",
                "OPENAI_API_BASE_URL": api_base_url,
                "OPENAI_API_KEY": (
                    config["gateway"]["authentication"]["api_key"]
                    if gateway_enabled
                    else "dummy"
                ),
            },
            "volumes": [
                "./data/open-webui:/app/backend/data",
            ],
            "networks": ["ai-network"],
        }

