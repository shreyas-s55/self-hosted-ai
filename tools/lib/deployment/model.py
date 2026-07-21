"""Deployment model definitions.

A deployment model represents a model exposed by THIS deployment.

It is intentionally separate from the built-in model catalog
(lib.models), which describes what models the platform knows about.

Example:

Deployment alias:
    chat

Built-in model:
    qwen-chat

Hugging Face repository:
    Qwen/Qwen2.5-7B-Instruct
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DeploymentModel:
    """A model exposed by the current deployment.

    Attributes:
        alias:
            Public name exposed through the API.
            Example: "chat", "coder", "reasoning"

        source:
            Name of the built-in model from MODEL_REGISTRY.
            Example: "qwen-chat"

        parameters:
            Runtime-specific parameters for this deployment.
            Example:
                dtype
                gpu_memory_utilization
                max_model_len
        """

    alias: str
    source: str
    parameters: dict[str, Any] = field(default_factory=dict)