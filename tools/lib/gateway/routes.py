"""Gateway route handlers.

Route handlers never interact with the runtime directly. Business logic
is delegated to :class:`GatewayService`, which coordinates request
processing and runtime communication.

Endpoints
---------
``GET /``
    Platform information.

``GET /health``
    Gateway health (always ``ok`` when the process is running).

``GET /v1/models``
    Available deployment aliases.

``POST /v1/chat/completions``
    OpenAI-compatible chat completion endpoint.
"""

import time

from fastapi import APIRouter, Request

from lib.gateway.health import check_deployments_health
from lib.gateway.models import (
    HealthResponse,
    ModelList,
    ModelObject,
    PlatformInfo,
)

router = APIRouter()


@router.get("/", response_model=PlatformInfo)
async def platform_info(request: Request) -> PlatformInfo:
    """Return platform metadata and current status."""
    settings = request.app.state.settings

    return PlatformInfo(
        version="0.1.0",
        runtime=settings.runtime,
        models=list(settings.aliases),
        status="ok",
    )


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    """Return gateway health."""
    deployments = request.app.state.deployments
    deployment_status = await check_deployments_health(deployments)

    overall = "ok"
    if deployment_status and any(v != "healthy" for v in deployment_status.values()):
        overall = "degraded"

    return HealthResponse(
        status=overall,
        deployments=deployment_status,
    )


@router.get("/v1/models", response_model=ModelList)
async def list_models(request: Request) -> ModelList:
    """Return the configured deployment aliases."""
    settings = request.app.state.settings

    return ModelList(
        data=[
            ModelObject(
                id=alias,
                created=int(time.time()),
                owned_by="self-hosted",
            )
            for alias in settings.aliases
        ]
    )


@router.post("/v1/chat/completions", response_model=None)
async def chat_completions(request: Request):
    """Handle an OpenAI-compatible chat completion request."""
    gateway = request.app.state.gateway
    return await gateway.chat_completions(request)