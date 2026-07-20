"""Runtime adapter registry.

To add a new runtime:

1. Create a new module in this package (e.g., ``sglang.py``).
2. Implement a subclass of :class:`RuntimeAdapter`.
3. Register it in ``_REGISTRY`` below.
"""

from lib.runtime.base import RuntimeAdapter
from lib.runtime.vllm import VLLMAdapter

_REGISTRY: dict[str, type[RuntimeAdapter]] = {
    "vllm": VLLMAdapter,
}

SUPPORTED_RUNTIMES = frozenset(_REGISTRY.keys())


def get_runtime_adapter(name: str) -> RuntimeAdapter:
    """Get a runtime adapter instance by engine name.

    Args:
        name: The runtime engine name (e.g., ``"vllm"``).

    Returns:
        An instance of the requested runtime adapter.

    Raises:
        ValueError: If the runtime engine is not supported.
    """
    adapter_cls = _REGISTRY.get(name)
    if adapter_cls is None:
        supported = ", ".join(sorted(SUPPORTED_RUNTIMES))
        raise ValueError(f"Unsupported runtime: '{name}'. Supported: {supported}")
    return adapter_cls()
