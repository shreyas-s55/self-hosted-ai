"""Gateway container entry point.

Uvicorn is invoked via CMD in the Dockerfile.  This module simply
exposes the ASGI ``app`` object created by the application factory.
"""

from lib.gateway.app import create_app

app = create_app()
