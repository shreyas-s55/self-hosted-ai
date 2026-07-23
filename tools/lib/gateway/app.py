"""FastAPI application factory for the AI gateway.

The app is configured entirely from environment variables so it can run
in any container environment without mounting a config file.

Required environment variables
-------------------------------
``GATEWAY_RUNTIME_URL``
    Base URL of the upstream runtime, e.g. ``http://vllm:8000/v1``.

``GATEWAY_MODELS``
    Comma-separated deployment aliases exposed by this gateway,
    e.g. ``"chat"`` or ``"chat,coder"``.

Optional environment variables
-------------------------------
``GATEWAY_RUNTIME``
    Human-readable runtime name surfaced in ``GET /``.
    Defaults to the hostname extracted from ``GATEWAY_RUNTIME_URL``.
"""

import os
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI

from lib.gateway.logging import LoggingMiddleware
from lib.gateway.middleware import (
    AuthenticationMiddleware,
    RequestIDMiddleware,
)
from lib.gateway.proxy import RuntimeProxy
from lib.gateway.routes import router
from lib.gateway.service import GatewayService
from lib.gateway.deployment import GatewayDeploymentRegistry
from lib.gateway.routing import RoutingService


@dataclass(frozen=True)
class GatewaySettings:
    """Immutable runtime configuration read from environment variables."""

    runtime_url: str
    runtime: str
    aliases: tuple[str, ...]


def _load_settings() -> GatewaySettings:
    runtime_url = os.environ["GATEWAY_RUNTIME_URL"]

    # Derive a human-readable runtime name from the URL host when not set.
    # "http://vllm:8000/v1" → "vllm"
    default_runtime = runtime_url.split("//")[-1].split(":")[0].split("/")[0]

    models_raw = os.environ.get("GATEWAY_MODELS", "")
    aliases = tuple(a.strip() for a in models_raw.split(",") if a.strip())

    return GatewaySettings(
        runtime_url=runtime_url,
        runtime=os.environ.get("GATEWAY_RUNTIME", default_runtime),
        aliases=aliases,
    )


def create_app() -> FastAPI:
    """Create and configure the FastAPI gateway application."""
    settings = _load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        proxy = RuntimeProxy(settings.runtime_url)

        deployments = GatewayDeploymentRegistry.from_environment()
        routing = RoutingService(deployments)

        gateway = GatewayService(
            proxy=proxy,
            router=routing,
        )

        app.state.settings = settings
        app.state.proxy = proxy
        app.state.gateway = gateway

        yield

        await proxy.close()

    app = FastAPI(
        title="self-hosted-ai",
        description="AI Gateway — OpenAI-compatible inference API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthenticationMiddleware)

    app.include_router(router)

    return app