"""Deployment resolver."""

from __future__ import annotations

from typing import Any

from lib.models import MODEL_REGISTRY
from lib.models.metadata import ModelMetadata

from .loader import load_models
from .model import DeploymentModel


class DeploymentResolver:
    """Resolves deployment aliases into platform model metadata."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._models = load_models(config)

    def resolve(self, alias: str) -> tuple[DeploymentModel, ModelMetadata]:
        """Resolve a deployment alias."""

        try:
            deployment = self._models[alias]
        except KeyError as exc:
            raise KeyError(
                f"Unknown deployment model '{alias}'."
            ) from exc

        metadata = MODEL_REGISTRY.get(deployment.source)

        if metadata is None:
            raise ValueError(
                f"Unknown model source '{deployment.source}'."
            )

        return deployment, metadata

    def list_models(self) -> dict[str, DeploymentModel]:
        """Return configured deployment models."""
        return dict(self._models)

    def aliases(self) -> list[str]:
        """Return deployment aliases."""
        return list(self._models.keys())

    def exists(self, alias: str) -> bool:
        """Return whether a deployment alias exists."""
        return alias in self._models