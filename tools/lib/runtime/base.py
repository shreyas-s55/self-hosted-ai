"""Abstract base class for inference runtime adapters."""

from abc import ABC, abstractmethod
from typing import Any


class RuntimeAdapter(ABC):
    """Base class for inference runtime adapters.

    Each adapter encapsulates the command-line interface of a specific
    inference engine, translating the unified project configuration into
    engine-specific arguments.

    Subclasses must implement:
        - image: container image for the runtime
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
    def build_command(self, config: dict[str, Any]) -> list[str]:
        """Generate runtime command-line arguments from configuration.

        Args:
            config: The full project configuration dictionary.

        Returns:
            A list of command-line arguments for the runtime process.
        """
