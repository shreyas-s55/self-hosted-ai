"""Service registry public API.

Usage::

    from lib.services import SERVICE_REGISTRY

    enabled = SERVICE_REGISTRY.enabled_services(config)
    for svc in enabled:
        name = svc.service_name(config)
        definition = svc.build(config)

To add a new service, see ``registry.py``.
"""

from lib.services.base import BaseService
from lib.services.registry import SERVICE_REGISTRY, ServiceRegistry

__all__ = ["SERVICE_REGISTRY", "BaseService", "ServiceRegistry"]
