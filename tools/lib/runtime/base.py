"""Abstract base class for inference runtime adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class RuntimeCapabilities:
    """Describes the capabilities of an inference runtime."""

    tool_calling: bool
    json_mode: bool
    structured_output: bool
    vision: bool
    embeddings: bool
    parallel_tool_calls: bool


class RuntimeAdapter(ABC):
    """Base class for inference runtime adapters."""

    @property
    @abstractmethod
    def image(self) -> str:
        """Container image for this runtime."""

    @property
    def health_endpoint(self) -> str:
        """Health check endpoint."""
        return "/health"

    @abstractmethod
    def capabilities(self) -> RuntimeCapabilities:
        """Return the capabilities supported by this runtime."""

    @abstractmethod
    def build_command(
        self,
        *,
        port: int,
        huggingface_repo: str,
        parameters: dict[str, Any],
        features: dict[str, Any],
    ) -> list[str]:
        """Build the runtime command.

        Args:
            port:
                Runtime API port.

            huggingface_repo:
                Fully-qualified HuggingFace repository.

            parameters:
                Deployment-specific runtime parameters.

            features:
                Enabled platform features from the configuration.

        Returns:
            Runtime-specific command line arguments.
        """