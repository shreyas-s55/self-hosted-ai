"""vLLM runtime adapter."""

from typing import Any

from lib.runtime.base import RuntimeAdapter


class VLLMAdapter(RuntimeAdapter):
    """Runtime adapter for the vLLM inference engine.

    Translates project configuration into vLLM CLI arguments including
    model parameters, server settings, and optional tool-calling support.
    """

    @property
    def image(self) -> str:
        return "vllm/vllm-openai:latest"

    def build_command(self, config: dict[str, Any]) -> list[str]:
        model = config["model"]
        runtime = config["runtime"]

        command = [
            "--model", str(model["name"]),
            "--host", "0.0.0.0",
            "--port", str(runtime["port"]),
            "--dtype", str(model["dtype"]),
            "--gpu-memory-utilization", str(model["gpu_memory_utilization"]),
            "--max-model-len", str(model["max_model_len"]),
        ]

        features = config.get("features", {})
        tool_calling = features.get("tool_calling", {})
        if tool_calling.get("enabled", False):
            command.extend([
                "--enable-auto-tool-choice",
                "--tool-call-parser", str(tool_calling["parser"]),
            ])

        return command
