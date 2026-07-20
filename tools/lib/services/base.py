"""Abstract base class for compose service definitions.

Each service is responsible solely for producing the compose definition
of exactly one logical service. Services do not know about each other,
do not write files, and do not serialize YAML.

Flow::

    ServiceRegistry.enabled_services(config)
        → [BaseService, ...]
        → compose_generator assembles final compose dict
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseService(ABC):
    """Base class for a single Docker Compose service definition.

    Subclasses own the full service spec: image, ports, volumes,
    environment, healthcheck, depends_on, and restart policy.

    Subclasses must implement:
        - name: stable identifier used by the registry
        - enabled: whether this service should be included
        - build: produce the compose service definition dict
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable identifier for this service type (used by the registry)."""

    def service_name(self, config: dict[str, Any]) -> str:
        """Return the key this service uses in the compose ``services`` block.

        Override when the compose service name is derived from configuration
        (e.g. the runtime service is named after the engine: ``"vllm"``).

        Args:
            config: The full project configuration dictionary.

        Returns:
            The string key for this service in the compose file.
        """
        return self.name

    @abstractmethod
    def enabled(self, config: dict[str, Any]) -> bool:
        """Return whether this service should be included in the generated compose.

        Args:
            config: The full project configuration dictionary.
        """

    @abstractmethod
    def build(self, config: dict[str, Any]) -> dict[str, Any]:
        """Produce the compose service definition dictionary.

        The returned dict is the value for this service's key in the
        compose ``services`` block. It must NOT be wrapped in
        ``{service_name: ...}`` — the registry and compose generator
        handle that.

        Args:
            config: The full project configuration dictionary.

        Returns:
            A compose service definition dictionary.
        """
