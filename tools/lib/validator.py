"""Configuration validator.

Validation runs in four passes:

1. Structural — required sections and field types.
2. Runtime compatibility — is the selected engine supported?
3. Model compatibility — if the model is in the registry, do its
   capabilities match the enabled features?
4. Feature compatibility — cross-check features against both the
   runtime engine and the model.
"""

from dataclasses import dataclass
from typing import Any

from lib.models import MODEL_REGISTRY
from lib.runtime import SUPPORTED_RUNTIMES, get_runtime_adapter


@dataclass
class ValidationError:
    """A single configuration validation error."""

    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.field}: {self.message}"


def validate_config(config: dict[str, Any]) -> list[ValidationError]:
    """Validate the project configuration.

    Args:
        config: The configuration dictionary.

    Returns:
        A list of validation errors. Empty if the configuration is valid.
    """
    errors: list[ValidationError] = []

    errors.extend(_validate_runtime(config))
    errors.extend(_validate_model(config))
    errors.extend(_validate_features(config))

    return errors


# ── Private helpers ────────────────────────────────────────────────────────────


def _validate_runtime(config: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    runtime = config.get("runtime")

    if runtime is None:
        errors.append(ValidationError("runtime", "Missing 'runtime' section"))
        return errors

    engine = runtime.get("engine")
    if not engine:
        errors.append(ValidationError("runtime.engine", "Missing 'engine'"))
    elif engine not in SUPPORTED_RUNTIMES:
        supported = ", ".join(sorted(SUPPORTED_RUNTIMES))
        errors.append(ValidationError(
            "runtime.engine",
            f"Unsupported engine '{engine}'. Supported: {supported}",
        ))

    port = runtime.get("port")
    if port is None:
        errors.append(ValidationError("runtime.port", "Missing 'port'"))
    elif not isinstance(port, int) or not (1 <= port <= 65535):
        errors.append(ValidationError(
            "runtime.port",
            f"Invalid port '{port}'. Must be an integer between 1 and 65535",
        ))

    return errors


def _validate_model(config: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    model = config.get("model")

    if model is None:
        errors.append(ValidationError("model", "Missing 'model' section"))
        return errors

    if not model.get("name"):
        errors.append(ValidationError("model.name", "Missing 'name'"))

    return errors


def _validate_features(config: dict[str, Any]) -> list[ValidationError]:
    """Cross-check enabled features against runtime and model capabilities."""
    errors: list[ValidationError] = []

    runtime_cfg = config.get("runtime", {})
    engine = runtime_cfg.get("engine")
    model_cfg = config.get("model", {})
    model_name = model_cfg.get("name", "")
    features = config.get("features", {})

    # Resolve runtime capabilities (skip if engine is invalid — already reported)
    runtime_caps = None
    if engine and engine in SUPPORTED_RUNTIMES:
        runtime_caps = get_runtime_adapter(engine).capabilities()

    # Resolve model metadata (None for unknown / full-repo configs)
    model_meta = MODEL_REGISTRY.get(model_name) if model_name else None

    # ── tool_calling ──────────────────────────────────────────────────────
    tool_calling = features.get("tool_calling", {})
    if tool_calling.get("enabled", False):
        if not tool_calling.get("parser"):
            errors.append(ValidationError(
                "features.tool_calling.parser",
                "Parser is required when tool calling is enabled",
            ))

        if runtime_caps is not None and not runtime_caps.tool_calling:
            errors.append(ValidationError(
                "features.tool_calling",
                f"Runtime '{engine}' does not support tool calling",
            ))

        if model_meta is not None and not model_meta.supports_tool_calling:
            errors.append(ValidationError(
                "features.tool_calling",
                f"Model '{model_meta.name}' ('{model_meta.huggingface_repo}') "
                "does not support tool calling. "
                "Set features.tool_calling.enabled: false or choose a compatible model.",
            ))

    # ── vision ────────────────────────────────────────────────────────────
    vision = features.get("vision", {})
    if vision.get("enabled", False):
        if runtime_caps is not None and not runtime_caps.vision:
            errors.append(ValidationError(
                "features.vision",
                f"Runtime '{engine}' does not support vision inputs",
            ))

        if model_meta is not None and not model_meta.supports_vision:
            errors.append(ValidationError(
                "features.vision",
                f"Model '{model_meta.name}' does not support vision inputs. "
                "Choose a vision-capable model (e.g. 'gemma') or disable this feature.",
            ))

    # ── reasoning profile ─────────────────────────────────────────────────
    reasoning = features.get("reasoning", {})
    if reasoning.get("enabled", False):
        if model_meta is not None and not model_meta.supports_reasoning:
            errors.append(ValidationError(
                "features.reasoning",
                f"Model '{model_meta.name}' does not support reasoning. "
                "Use a reasoning model (e.g. 'deepseek-r1-distill') or disable this feature.",
            ))

    return errors

