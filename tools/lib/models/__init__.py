"""Model registry public API.

Usage::

    from lib.models import MODEL_REGISTRY

    # Look up by short name or full repo
    metadata = MODEL_REGISTRY.get("qwen-chat")
    metadata = MODEL_REGISTRY.get("Qwen/Qwen2.5-7B-Instruct")

    # Resolve a name from config.yaml to the HuggingFace repo
    repo = MODEL_REGISTRY.resolve_repo(config["model"]["name"])
"""

from lib.models.builtins import BUILTIN_MODELS
from lib.models.metadata import ModelMetadata
from lib.models.registry import ModelRegistry

MODEL_REGISTRY = ModelRegistry(BUILTIN_MODELS)

__all__ = ["MODEL_REGISTRY", "ModelMetadata", "ModelRegistry"]
