"""Certified model catalog.

Add new model entries here. Each entry must have an accurate
``huggingface_repo`` and correct capability flags — the validator
relies on these values to catch configuration errors before deployment.

When exact values are unknown, use conservative defaults and mark
the entry with a comment.
"""

from lib.models.metadata import ModelMetadata

BUILTIN_MODELS: tuple[ModelMetadata, ...] = (

    # ──────────────────────────────────────────────────────────────────────
    # Qwen
    # ──────────────────────────────────────────────────────────────────────

    ModelMetadata(
        name="qwen-chat-1.5b",
        family="qwen",
        huggingface_repo="Qwen/Qwen2.5-1.5B-Instruct",
        runtime="vllm",
        context_length=32768,
        min_gpu_memory_gb=4.0,
        supports_chat=True,
        supports_tool_calling=True,
        supports_structured_output=True,
        supports_json_mode=True,
        supports_embeddings=False,
        supports_reasoning=False,
        supports_vision=False,
        default_parameters={
            "dtype": "auto",
            "gpu_memory_utilization": 0.27,
            "max_model_len": 8192,
            "enforce_eager": True,
        },
    ),

    ModelMetadata(
        name="qwen-chat",
        family="qwen",
        huggingface_repo="Qwen/Qwen2.5-7B-Instruct",
        runtime="vllm",
        context_length=131072,
        min_gpu_memory_gb=16.0,
        supports_chat=True,
        supports_tool_calling=True,
        supports_structured_output=True,
        supports_json_mode=True,
        supports_embeddings=False,
        supports_reasoning=False,
        supports_vision=False,
        default_parameters={
            "dtype": "auto",
            "gpu_memory_utilization": 0.90,
            "max_model_len": 8192,
        },
    ),

    ModelMetadata(
        name="qwen-coder-1.5b",
        family="qwen",
        huggingface_repo="Qwen/Qwen2.5-Coder-1.5B-Instruct",
        runtime="vllm",
        context_length=32768,
        min_gpu_memory_gb=4.0,
        supports_chat=True,
        supports_tool_calling=True,
        supports_structured_output=True,
        supports_json_mode=True,
        supports_embeddings=False,
        supports_reasoning=False,
        supports_vision=False,
        default_parameters={
            "dtype": "auto",
            "gpu_memory_utilization": 0.27,
            "max_model_len": 8192,
            "enforce_eager": True,
        },
    ),

    ModelMetadata(
        name="qwen-coder",
        family="qwen",
        huggingface_repo="Qwen/Qwen2.5-Coder-7B-Instruct",
        runtime="vllm",
        context_length=131072,
        min_gpu_memory_gb=16.0,
        supports_chat=True,
        supports_tool_calling=True,
        supports_structured_output=True,
        supports_json_mode=True,
        supports_embeddings=False,
        supports_reasoning=False,
        supports_vision=False,
        default_parameters={
            "dtype": "auto",
            "gpu_memory_utilization": 0.90,
            "max_model_len": 8192,
        },
    ),

    # ──────────────────────────────────────────────────────────────────────
    # DeepSeek
    # ──────────────────────────────────────────────────────────────────────

    ModelMetadata(
        name="deepseek-r1-distill-1.5b",
        family="deepseek",
        huggingface_repo="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        runtime="vllm",
        context_length=32768,
        min_gpu_memory_gb=4.0,
        supports_chat=True,
        supports_tool_calling=False,
        supports_structured_output=False,
        supports_json_mode=True,
        supports_embeddings=False,
        supports_reasoning=True,
        supports_vision=False,
        default_parameters={
            "dtype": "auto",
            "gpu_memory_utilization": 0.27,
            "max_model_len": 8192,
            "enforce_eager": True,
        },
    ),

    ModelMetadata(
        name="deepseek-r1-distill",
        family="deepseek",
        huggingface_repo="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        runtime="vllm",
        context_length=131072,
        min_gpu_memory_gb=16.0,
        supports_chat=True,
        supports_tool_calling=False,
        supports_structured_output=False,
        supports_json_mode=True,
        supports_embeddings=False,
        supports_reasoning=True,
        supports_vision=False,
        default_parameters={
            "dtype": "auto",
            "gpu_memory_utilization": 0.90,
            "max_model_len": 8192,
        },
    ),

    ModelMetadata(
        name="deepseek-coder",
        family="deepseek",
        huggingface_repo="deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
        runtime="vllm",
        context_length=163840,
        min_gpu_memory_gb=24.0,
        supports_chat=True,
        supports_tool_calling=True,
        supports_structured_output=True,
        supports_json_mode=True,
        supports_embeddings=False,
        supports_reasoning=False,
        supports_vision=False,
        default_parameters={
            "dtype": "auto",
            "gpu_memory_utilization": 0.90,
            "max_model_len": 8192,
        },
    ),

    # ──────────────────────────────────────────────────────────────────────
    # Gemma
    # ──────────────────────────────────────────────────────────────────────

    ModelMetadata(
        name="gemma",
        family="gemma",
        huggingface_repo="google/gemma-3-4b-it",
        runtime="vllm",
        context_length=131072,
        min_gpu_memory_gb=10.0,
        supports_chat=True,
        supports_tool_calling=False,
        supports_structured_output=False,
        supports_json_mode=True,
        supports_embeddings=False,
        supports_reasoning=False,
        supports_vision=True,
        default_parameters={
            "dtype": "auto",
            "gpu_memory_utilization": 0.90,
            "max_model_len": 8192,
        },
    ),

    # ──────────────────────────────────────────────────────────────────────
    # Llama
    # ──────────────────────────────────────────────────────────────────────

    ModelMetadata(
        name="llama",
        family="llama",
        huggingface_repo="meta-llama/Llama-3.1-8B-Instruct",
        runtime="vllm",
        context_length=131072,
        min_gpu_memory_gb=16.0,
        supports_chat=True,
        supports_tool_calling=True,
        supports_structured_output=True,
        supports_json_mode=True,
        supports_embeddings=False,
        supports_reasoning=False,
        supports_vision=False,
        default_parameters={
            "dtype": "auto",
            "gpu_memory_utilization": 0.90,
            "max_model_len": 8192,
        },
    ),
)
