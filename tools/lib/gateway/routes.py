"""Gateway route handlers.

Route handlers never interact with the runtime directly.  Proxy
operations go through :class:`RuntimeProxy`; model lookups go through
the Model Registry.  Both are accessed from ``request.app.state``,
populated by the application lifespan in :mod:`lib.gateway.app`.

Endpoints
---------
``GET /``
    Platform information.

``GET /health``
    Gateway health (always ``ok`` when the process is running).

``GET /v1/models``
    Available models from the Model Registry.
    Does NOT call the runtime.

``POST /v1/chat/completions``
    Transparent proxy to the runtime.
"""

import time

from fastapi import APIRouter, Request
from fastapi.responses import Response, StreamingResponse

from lib.gateway.models import HealthResponse, ModelList, ModelObject, PlatformInfo

router = APIRouter()


@router.get("/", response_model=PlatformInfo)
async def platform_info(request: Request) -> PlatformInfo:
    """Return platform metadata and current status."""
    s = request.app.state.settings
    return PlatformInfo(
        version="0.1.0",
        runtime=s.runtime,
        model=s.model_name,
        status="ok",
    )


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return gateway health.  ``ok`` indicates the process is running."""
    return HealthResponse(status="ok")


@router.get("/v1/models", response_model=ModelList)
async def list_models(request: Request) -> ModelList:
    """Return the loaded model from the Model Registry.

    This endpoint does NOT call the upstream runtime.  It returns
    metadata from the registry for the model configured at startup.
    """
    from lib.models import MODEL_REGISTRY

    s = request.app.state.settings
    metadata = MODEL_REGISTRY.get(s.model_name)

    return ModelList(
        data=[
            ModelObject(
                id=s.model_name,
                created=int(time.time()),
                owned_by=metadata.family if metadata else "self-hosted",
            )
        ]
    )


@router.post("/v1/chat/completions", response_model=None)
async def chat_completions(request: Request) -> Response:
    """Proxy chat completion requests to the upstream runtime.

    The gateway does not inspect or modify the request body — it is
    forwarded verbatim.  Streaming is detected from ``"stream": true``
    in the request body and handled transparently.
    """
    return await request.app.state.proxy.forward(request, "/chat/completions")
