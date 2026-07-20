"""AI Gateway public API.

Usage (application factory)::

    from lib.gateway.app import create_app

    app = create_app()

The application reads its configuration from environment variables —
see :mod:`lib.gateway.app` for the full list.
"""

from lib.gateway.app import GatewaySettings, create_app

__all__ = ["create_app", "GatewaySettings"]
