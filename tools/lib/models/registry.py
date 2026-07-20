"""Model registry — lookup and name resolution."""

from typing import Iterator

from lib.models.metadata import ModelMetadata


class ModelRegistry:
    """Registry mapping short model names and HuggingFace repos to metadata.

    Both the short name (``"qwen-chat"``) and the full HuggingFace repo
    (``"Qwen/Qwen2.5-7B-Instruct"``) are accepted as lookup keys so that
    existing configs using full repo names keep working unchanged.

    Example::

        metadata = registry.get("qwen-chat")
        metadata = registry.get("Qwen/Qwen2.5-7B-Instruct")  # same result
    """

    def __init__(self, models: tuple[ModelMetadata, ...]) -> None:
        self._by_name: dict[str, ModelMetadata] = {m.name: m for m in models}
        self._by_repo: dict[str, ModelMetadata] = {m.huggingface_repo: m for m in models}

    def get(self, name: str) -> ModelMetadata | None:
        """Return metadata for a short name or HuggingFace repo, or ``None``."""
        return self._by_name.get(name) or self._by_repo.get(name)

    def resolve_repo(self, name: str) -> str:
        """Resolve a short model name to the full HuggingFace repo.

        If ``name`` is already a full repo or is not in the registry, it is
        returned unchanged — preserving backward compatibility.
        """
        metadata = self.get(name)
        return metadata.huggingface_repo if metadata else name

    def __iter__(self) -> Iterator[ModelMetadata]:
        return iter(self._by_name.values())

    def __len__(self) -> int:
        return len(self._by_name)
