"""Runtime inference service definition.

The service name in compose is the engine name (e.g. ``"vllm"``),
derived at build time from ``config["runtime"]["engine"]``.

All runtime-specific command generation is delegated to the
:class:`RuntimeAdapter`. This service only assembles the compose
service definition around the adapter output.
"""

from typing import Any

from lib.deployment import DeploymentResolver, is_multi_mode
from lib.models.metadata import ModelMetadata
from lib.runtime import get_runtime_adapter
from lib.services.base import BaseService


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
        # In multi mode, RuntimeService is expanded by iter_builds.
        if is_multi_mode(config):
            return self._build_for_alias(config, DeploymentResolver(config).default().deployment.alias)

        runtime = config["runtime"]
        engine = runtime["engine"]
        resolver = DeploymentResolver(config)
        resolved = resolver.default()

        return self._build_runtime_service(
            config=config,
            service_name=engine,
            container_name=engine,
            hostname=engine,
            runtime_engine=engine,
            port=runtime["port"],
            source=resolved.metadata.huggingface_repo,
            parameters=resolved.deployment.parameters,
        )

    def iter_builds(self, config: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
        """Return one or many compose runtime service definitions."""

        if not is_multi_mode(config):
            return [(self.service_name(config), self.build(config))]

        resolver = DeploymentResolver(config)

        builds: list[tuple[str, dict[str, Any]]] = []

        for alias in resolver.aliases():
            builds.append((f"runtime-{alias}", self._build_for_alias(config, alias)))

        return builds

    def _build_for_alias(self, config: dict[str, Any], alias: str) -> dict[str, Any]:
        runtime = config["runtime"]
        resolver = DeploymentResolver(config)
        resolved = resolver.resolve(alias)

        runtime_engine = resolved.deployment.runtime or runtime["engine"]
        port = runtime["port"]

        service_name = runtime_engine if not is_multi_mode(config) else f"runtime-{alias}"

        # Only pass feature flags that this specific model supports.
        # Each deployment is autonomous — capabilities are per-model.
        features = _filter_features(config.get("features", {}), resolved.metadata)

        return self._build_runtime_service(
            config=config,
            service_name=service_name,
            container_name=service_name,
            hostname=service_name,
            runtime_engine=runtime_engine,
            port=port,
            source=resolved.metadata.huggingface_repo,
            parameters=resolved.deployment.parameters,
            features=features,
        )

    def _build_runtime_service(
        self,
        *,
        config: dict[str, Any],
        service_name: str,
        container_name: str,
        hostname: str,
        runtime_engine: str,
        port: int,
        source: str,
        parameters: dict[str, Any],
        features: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        adapter = get_runtime_adapter(runtime_engine)

        command = adapter.build_command(
            port=port,
            huggingface_repo=source,
            parameters=parameters,
            features=features if features is not None else config.get("features", {}),
        )

        healthcheck_script = (
            "import urllib.request; "
            f"urllib.request.urlopen('http://localhost:{port}{adapter.health_endpoint}')"
        )

        return {
            "image": adapter.image,
            "container_name": container_name,
            "hostname": hostname,
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


def _filter_features(
    features: dict[str, Any],
    metadata: ModelMetadata,
) -> dict[str, Any]:
    """Return a shallow copy of features with flags disabled for unsupported capabilities.

    Each deployment is responsible only for what its model supports.
    Callers set global feature flags; this function enforces per-model boundaries.
    """
    filtered = dict(features)

    tool_calling = filtered.get("tool_calling", {})
    if tool_calling.get("enabled") and not metadata.supports_tool_calling:
        filtered["tool_calling"] = {**tool_calling, "enabled": False}

    vision = filtered.get("vision", {})
    if vision.get("enabled") and not metadata.supports_vision:
        filtered["vision"] = {**vision, "enabled": False}

    return filtered