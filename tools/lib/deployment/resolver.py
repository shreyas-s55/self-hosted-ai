"""Deployment resolver.

This module bridges two distinct layers:

* **Deployment layer** (:class:`DeploymentModel`) — what *this specific
  deployment* exposes: a public alias (e.g. ``"chat"``), the backing
  source name from the platform catalog (e.g. ``"qwen-chat"``), and
  per-deployment runtime parameters such as dtype and context length.

* **Platform catalog** (:class:`~lib.models.metadata.ModelMetadata`) —
  canonical model information that does not change between deployments:
  the HuggingFace repository path, capability flags, minimum GPU memory
  requirements, and model family metadata.

A :class:`ResolvedDeployment` combines both into a single typed object
returned by :meth:`DeploymentResolver.resolve`.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from lib.models import MODEL_REGISTRY
from lib.models.metadata import ModelMetadata

from .loader import load_models
from .model import DeploymentModel
from lib.application import DeploymentProvider

@dataclass(frozen=True, slots=True)
class ResolvedDeployment:
    """A fully resolved deployment model.

    Combines the deployment-specific configuration with the canonical
    platform model metadata.
    """

    deployment: DeploymentModel
    metadata: ModelMetadata


class DeploymentResolver(DeploymentProvider):
    """Resolves deployment aliases into platform model metadata.

    Deployment models are loaded once during construction and cached for
    constant-time lookups thereafter.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self._models: Mapping[str, DeploymentModel] = MappingProxyType(
            load_models(config)
        )

    def resolve(self, alias: str) -> ResolvedDeployment:
        """Resolve a deployment alias."""

        try:
            deployment = self._models[alias]
        except KeyError as exc:
            raise KeyError(
                f"Unknown deployment alias '{alias}'."
            ) from exc

        metadata = MODEL_REGISTRY.get(deployment.source)

        if metadata is None:
            metadata = ModelMetadata(
                name=deployment.source,
                family="custom",
                huggingface_repo=deployment.source,
                runtime=deployment.runtime or "unknown",
                context_length=0,
                min_gpu_memory_gb=0.0,
                supports_chat=True,
                supports_tool_calling=False,
                supports_structured_output=False,
                supports_json_mode=False,
                supports_embeddings=False,
                supports_reasoning=False,
                supports_vision=False,
                default_parameters={},
            )

        return ResolvedDeployment(
            deployment=deployment,
            metadata=metadata,
        )

    def default(self) -> ResolvedDeployment:
        """Return the default deployment.

        For now, the default is simply the first deployment declared in
        the configuration. This can later evolve into an explicit
        configuration option.
        """

        for alias, deployment in self._models.items():
            if deployment.default:
                return self.resolve(alias)

        try:
            alias = next(iter(self._models))
        except StopIteration as exc:
            raise ValueError(
                "No deployment models are configured."
            ) from exc

        return self.resolve(alias)

    def aliases(self) -> tuple[str, ...]:
        """Return configured deployment aliases."""
        return tuple(self._models.keys())

    def deployments(self) -> dict[str, DeploymentModel]:
        """Return a snapshot of configured deployment models."""
        return dict(self._models)