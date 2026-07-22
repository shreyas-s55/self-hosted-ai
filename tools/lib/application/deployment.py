"""Application-level deployment contracts."""

from __future__ import annotations

from typing import Any, Protocol


class DeploymentProvider(Protocol):
    """Provides deployment resolution to the application layer."""

    def resolve(self, alias: str) -> Any:
        """Resolve a deployment alias."""
        ...

    def default(self) -> Any:
        """Return the default deployment."""
        ...

    def aliases(self) -> tuple[str, ...]:
        """Return available deployment aliases."""
        ...