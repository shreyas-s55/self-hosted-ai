"""Open WebUI service definition."""

from typing import Any

from lib.services.base import BaseService


class OpenWebUIService(BaseService):
    """Compose service definition for Open WebUI."""

    @property
    def name(self) -> str:
        return "open-webui"

    def enabled(self, config: dict[str, Any]) -> bool:
        return config.get("ui", {}).get("enabled", True)

    def build(self, config: dict[str, Any]) -> dict[str, Any]:
        runtime = config["runtime"]
        engine = runtime["engine"]
        port = runtime["port"]

        return {
            "image": "ghcr.io/open-webui/open-webui:main",
            "container_name": "open-webui",
            "restart": "unless-stopped",
            "depends_on": {
                engine: {"condition": "service_healthy"},
            },
            "expose": ["8080"],
            "environment": {
                "TZ": "${TZ}",
                "OPENAI_API_BASE_URL": f"http://{engine}:{port}/v1",
                "OPENAI_API_KEY": "dummy",
            },
            "volumes": [
                "./data/open-webui:/app/backend/data",
            ],
            "networks": ["ai-network"],
        }
