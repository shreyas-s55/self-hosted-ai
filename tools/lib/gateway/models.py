"""Pydantic models for the gateway API.

These models define the public contract of the gateway endpoints.
They are intentionally minimal — the proxy endpoints forward the
raw body, so request validation is left to the upstream runtime.
"""

import time
from typing import Any

from pydantic import BaseModel, Field


class PlatformInfo(BaseModel):
    """Response for ``GET /``."""

    platform: str = "self-hosted-ai"
    version: str
    runtime: str
    models: list[str]
    status: str


class HealthResponse(BaseModel):
    """Response for ``GET /health``."""

    status: str
    deployments: dict[str, str] | None = None


class ModelObject(BaseModel):
    """A single model entry in the OpenAI models list format."""

    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "self-hosted"


class ModelList(BaseModel):
    """Response for ``GET /v1/models``."""

    object: str = "list"
    data: list[ModelObject]
