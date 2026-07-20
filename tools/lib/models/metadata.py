"""Model metadata types.

ModelMetadata describes what a model can do at the capability level.
RuntimeCapabilities (in runtime/base.py) describes what a runtime engine supports.
The validator cross-checks both to catch mismatches before deployment.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ModelMetadata:
    """Immutable capability record for a certified model.

    Fields use the ``supports_*`` naming convention to make capability
    checks read naturally in the validator::

        if not metadata.supports_tool_calling:
            errors.append(...)
    """

    name: str
    """Short identifier used in config.yaml, e.g. ``"qwen-chat"``."""

    family: str
    """Model family, e.g. ``"qwen"``, ``"deepseek"``, ``"llama"``."""

    huggingface_repo: str
    """Full HuggingFace repository identifier, e.g. ``"Qwen/Qwen2.5-7B-Instruct"``."""

    runtime: str
    """Recommended inference runtime, e.g. ``"vllm"``."""

    context_length: int
    """Maximum context window in tokens."""

    min_gpu_memory_gb: float
    """Minimum GPU VRAM required to load the model (in GB)."""

    supports_chat: bool
    """Model follows a chat/instruction-following format."""

    supports_tool_calling: bool
    """Model can invoke external tools / function calling."""

    supports_structured_output: bool
    """Model can produce structured output (e.g. Pydantic schemas)."""

    supports_json_mode: bool
    """Model reliably produces valid JSON when asked."""

    supports_embeddings: bool
    """Model can be used for dense vector embeddings."""

    supports_reasoning: bool
    """Model performs chain-of-thought / reasoning (e.g. DeepSeek R1)."""

    supports_vision: bool
    """Model accepts image inputs."""

    default_parameters: dict[str, Any] = field(default_factory=dict)
    """Suggested runtime parameters for this model (dtype, gpu_memory_utilization, etc.)."""
