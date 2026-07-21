"""Configuration validator.

Validation runs in four passes:

1. Structural — required sections and field types.
2. Runtime compatibility — is the selected engine supported?
3. Deployment models — do all configured aliases resolve in the catalog?
4. Feature compatibility — cross-check features against both the
   runtime engine and every deployed model.
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
    errors.extend(_validate_deployments(config))
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


def _validate_deployments(config: dict[str, Any]) -> list[ValidationError]:
    """Validate the ``models`` section against the platform model catalog."""
    errors: list[ValidationError] = []

    models_cfg = config.get("models")

    if models_cfg is None:
        errors.append(ValidationError("models", "Missing 'models' section"))
        return errors

    if not isinstance(models_cfg, dict):
        errors.append(ValidationError("models", "'models' must be a mapping"))
        return errors

    if not models_cfg:
        errors.append(ValidationError("models", "At least one deployment model is required"))
        return errors

    for alias, model_cfg in models_cfg.items():
        if not isinstance(model_cfg, dict):
            errors.append(ValidationError(
                f"models.{alias}",
                "Must be a mapping with at least a 'source' key",
            ))
            continue

        source = model_cfg.get("source")
        if not source:
            errors.append(ValidationError(
                f"models.{alias}.source",
                "Missing required field 'source'",
            ))
            continue

        if MODEL_REGISTRY.get(source) is None:
            errors.append(ValidationError(
                f"models.{alias}.source",
                f"Unknown model source '{source}'. Not found in the model catalog.",
            ))

        params = model_cfg.get("parameters", {})
        if params is not None and not isinstance(params, dict):
            errors.append(ValidationError(
                f"models.{alias}.parameters",
                "'parameters' must be a mapping",
            ))

    return errors


def _validate_features(config: dict[str, Any]) -> list[ValidationError]:
    """Cross-check enabled features against runtime and model capabilities."""
    errors: list[ValidationError] = []

    engine = config.get("runtime", {}).get("engine")
    features = config.get("features", {})

    # Resolve runtime capabilities (skip if engine is invalid — already reported)
    runtime_caps = None
    if engine and engine in SUPPORTED_RUNTIMES:
        runtime_caps = get_runtime_adapter(engine).capabilities()

    # Collect metadata for every deployed model that resolves in the catalog
    deployed_meta = []
    for alias, model_cfg in config.get("models", {}).items():
        if isinstance(model_cfg, dict):
            source = model_cfg.get("source", "")
            meta = MODEL_REGISTRY.get(source) if source else None
            if meta is not None:
                deployed_meta.append((alias, meta))

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

        for alias, meta in deployed_meta:
            if not meta.supports_tool_calling:
                errors.append(ValidationError(
                    "features.tool_calling",
                    f"Model '{alias}' ('{meta.huggingface_repo}') does not support tool calling. "
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

        for alias, meta in deployed_meta:
            if not meta.supports_vision:
                errors.append(ValidationError(
                    "features.vision",
                    f"Model '{alias}' ('{meta.name}') does not support vision inputs. "
                    "Choose a vision-capable model or disable this feature.",
                ))

    # ── reasoning ─────────────────────────────────────────────────────────
    reasoning = features.get("reasoning", {})
    if reasoning.get("enabled", False):
        for alias, meta in deployed_meta:
            if not meta.supports_reasoning:
                errors.append(ValidationError(
                    "features.reasoning",
                    f"Model '{alias}' ('{meta.name}') does not support reasoning. "
                    "Use a reasoning model (e.g. 'deepseek-r1-distill') or disable this feature.",
                ))

    return errors

