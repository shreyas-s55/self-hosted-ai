"""Gateway routing domain."""

from lib.gateway.routing.rules import classify
from lib.gateway.routing.service import RoutingService

__all__ = ["RoutingService", "classify"]