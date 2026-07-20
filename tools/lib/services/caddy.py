"""Caddy reverse-proxy service definition."""

from typing import Any

from lib.services.base import BaseService


class CaddyService(BaseService):
    """Compose service definition for the Caddy reverse proxy."""

    @property
    def name(self) -> str:
        return "caddy"

    def enabled(self, config: dict[str, Any]) -> bool:
        return config.get("ui", {}).get("enabled", True)

    def build(self, config: dict[str, Any]) -> dict[str, Any]:
        return {
            "image": "caddy:2.10",
            "container_name": "caddy",
            "restart": "unless-stopped",
            "ports": ["80:80"],
            "depends_on": ["open-webui"],
            "volumes": [
                "./caddy/Caddyfile:/etc/caddy/Caddyfile:ro",
                "./data/caddy:/data",
                "./data/caddy:/config",
            ],
            "networks": ["ai-network"],
        }
