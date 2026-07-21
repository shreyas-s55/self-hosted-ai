"""Runtime inference service definition.

The service name in compose is the engine name (e.g. ``"vllm"``),
derived at build time from ``config["runtime"]["engine"]``.

All runtime-specific command generation is delegated to the
:class:`RuntimeAdapter` — this service only assembles the compose
service dict around the adapter's output.
"""

from typing import Any

from lib.deployment import DeploymentResolver
from lib.runtime import get_runtime_adapter
from lib.services.base import BaseService

# Primary deployment alias used for the runtime service.
# A single runtime instance serves the first configured deployment model.
# This is intentionally hardcoded until multi-instance routing is supported.
_PRIMARY_ALIAS = "chat"


class RuntimeService(BaseService):
    """Compose service definition for the inference runtime."""

    @property
    def name(self) -> str:
        return "runtime"

    def service_name(self, config: dict[str, Any]) -> str:
        return config["runtime"]["engine"]

    def enabled(self, config: dict[str, Any]) -> bool:
        return bool(config.get("runtime", {}).get("engine"))

    def build(self, config: dict[str, Any]) -> dict[str, Any]:
        runtime = config["runtime"]
        port = runtime["port"]

        resolver = DeploymentResolver(config)
        deployment, metadata = resolver.resolve(_PRIMARY_ALIAS)

        adapter = get_runtime_adapter(runtime["engine"])
        command = adapter.build_command(config, metadata.huggingface_repo, deployment.parameters)

        healthcheck_script = (
            "import urllib.request; "
            f"urllib.request.urlopen('http://localhost:{port}{adapter.health_endpoint}')"
        )

        return {
            "image": adapter.image,
            "container_name": runtime["engine"],
            "restart": "unless-stopped",
            "runtime": "nvidia",
            "ipc": "host",
            "command": command,
            "environment": {
                "HUGGING_FACE_HUB_TOKEN": "${HF_TOKEN}",
            },
            "volumes": [
                f"{config['storage']['download_dir']}:/root/.cache/huggingface",
            ],
            "expose": [str(port)],
            "healthcheck": {
                "test": ["CMD", "python3", "-c", healthcheck_script],
                "interval": "10s",
                "timeout": "5s",
                "retries": 60,
                "start_period": "120s",
            },
            "networks": ["ai-network"],
        }
