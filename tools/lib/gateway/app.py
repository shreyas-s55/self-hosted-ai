"""FastAPI application factory for the AI gateway.

The app is configured entirely from environment variables so it can run
in any container environment without mounting a config file.

Required environment variables
-------------------------------
``GATEWAY_RUNTIME_URL``
    Base URL of the upstream runtime, e.g. ``http://vllm:8000/v1``.

``GATEWAY_MODEL_NAME``
    Name of the loaded model, e.g. ``Qwen/Qwen2.5-7B-Instruct``.

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

from lib.gateway.middleware import (
    AuthenticationMiddleware,
    RequestIDMiddleware,
)
from lib.gateway.proxy import RuntimeProxy
from lib.gateway.routes import router


@dataclass(frozen=True)
class GatewaySettings:
    """Immutable runtime configuration read from environment variables."""

    runtime_url: str
    runtime: str
    model_name: str


def _load_settings() -> GatewaySettings:
    runtime_url = os.environ["GATEWAY_RUNTIME_URL"]
    # Derive a human-readable runtime name from the URL host when not set.
    # "http://vllm:8000/v1" → "vllm"
    default_runtime = runtime_url.split("//")[-1].split(":")[0].split("/")[0]
    return GatewaySettings(
        runtime_url=runtime_url,
        runtime=os.environ.get("GATEWAY_RUNTIME", default_runtime),
        model_name=os.environ["GATEWAY_MODEL_NAME"],
    )


def create_app() -> FastAPI:
    """Create and configure the FastAPI gateway application.

    Returns:
        A fully configured :class:`FastAPI` instance.
    """
    settings = _load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        proxy = RuntimeProxy(settings.runtime_url)
        app.state.settings = settings
        app.state.proxy = proxy
        yield
        await proxy.close()

    app = FastAPI(
        title="self-hosted-ai",
        description="AI Gateway — OpenAI-compatible inference API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(AuthenticationMiddleware)
    app.include_router(router)
    return app
