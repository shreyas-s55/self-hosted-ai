"""vLLM runtime adapter."""

from typing import Any

from lib.runtime.base import RuntimeAdapter, RuntimeCapabilities


class VLLMAdapter(RuntimeAdapter):
    """Runtime adapter for the vLLM inference engine."""

    @property
    def image(self) -> str:
        return "vllm/vllm-openai:latest"

    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(
            tool_calling=True,
            json_mode=True,
            structured_output=True,
            vision=True,
            embeddings=True,
            parallel_tool_calls=True,
        )

    def build_command(
        self,
        *,
        port: int,
        huggingface_repo: str,
        parameters: dict[str, Any],
        features: dict[str, Any],
    ) -> list[str]:
        """Build the vLLM command line."""

        command = [
            "--model",
            huggingface_repo,
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
            "--dtype",
            str(parameters.get("dtype", "auto")),
            "--gpu-memory-utilization",
            str(parameters.get("gpu_memory_utilization", 0.90)),
            "--max-model-len",
            str(parameters.get("max_model_len", 8192)),
        ]

        if parameters.get("enforce_eager", False):
            command.append("--enforce-eager")

        tool_calling = features.get("tool_calling", {})

        if tool_calling.get("enabled", False):
            command.extend(
                [
                    "--enable-auto-tool-choice",
                    "--tool-call-parser",
                    str(tool_calling["parser"]),
                ]
            )

        return command