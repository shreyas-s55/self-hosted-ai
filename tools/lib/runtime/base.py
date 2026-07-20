"""Abstract base class for inference runtime adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuntimeCapabilities:
    """Describes what an inference runtime engine supports.

    These are engine-level capabilities independent of any specific model.
    The validator cross-checks these against :class:`ModelMetadata` and the
    enabled features in ``config.yaml`` to catch mismatches before deployment.
    """

    tool_calling: bool
    """Engine supports tool / function calling."""

    json_mode: bool
    """Engine can constrain output to valid JSON."""

    structured_output: bool
    """Engine supports schema-guided structured output (e.g. Pydantic)."""

    vision: bool
    """Engine can process image inputs."""

    embeddings: bool
    """Engine can produce dense vector embeddings."""

    parallel_tool_calls: bool
    """Engine can invoke multiple tools in a single turn."""


class RuntimeAdapter(ABC):
    """Base class for inference runtime adapters.

    Each adapter encapsulates the command-line interface of a specific
    inference engine, translating the unified project configuration into
    engine-specific arguments.

    Subclasses must implement:
        - image: container image for the runtime
        - capabilities: engine-level capability declaration
        - build_command: generate CLI arguments from config
    """

    @property
    @abstractmethod
    def image(self) -> str:
        """Container image for this runtime."""

    @property
    def health_endpoint(self) -> str:
        """Health check URL path for the runtime."""
        return "/health"

    @abstractmethod
    def capabilities(self) -> RuntimeCapabilities:
        """Return the capabilities of this runtime engine.

        Returns:
            A :class:`RuntimeCapabilities` instance describing what the
            engine supports independently of any specific model.
        """

    @abstractmethod
    def build_command(self, config: dict[str, Any]) -> list[str]:
        """Generate runtime command-line arguments from configuration.

        Args:
            config: The full project configuration dictionary.

        Returns:
            A list of command-line arguments for the runtime process.
        """
