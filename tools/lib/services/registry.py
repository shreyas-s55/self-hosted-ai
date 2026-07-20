"""Service registry — ordered collection of all compose services.

To add a new service:

1. Create ``tools/lib/services/<service>.py``.
2. Implement a subclass of :class:`BaseService`.
3. Import it and add an instance to ``_SERVICES`` below.

Services are returned in registration order, which determines their
position in the generated compose file.
"""

from typing import Any

from lib.services.base import BaseService
from lib.services.runtime import RuntimeService
from lib.services.webui import OpenWebUIService
from lib.services.caddy import CaddyService

_SERVICES: tuple[BaseService, ...] = (
    RuntimeService(),
    OpenWebUIService(),
    CaddyService(),
)


class ServiceRegistry:
    """Registry of all compose services.

    Holds an ordered sequence of :class:`BaseService` instances and
    filters them to only those enabled for a given configuration.
    """

    def __init__(self, services: tuple[BaseService, ...]) -> None:
        self._services = services

    def enabled_services(self, config: dict[str, Any]) -> list[BaseService]:
        """Return services that are enabled for the given configuration.

        Args:
            config: The full project configuration dictionary.

        Returns:
            An ordered list of enabled :class:`BaseService` instances.
        """
        return [svc for svc in self._services if svc.enabled(config)]


SERVICE_REGISTRY = ServiceRegistry(_SERVICES)
