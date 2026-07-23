"""Configuration validator."""

from dataclasses import dataclass
from typing import Any

from lib.deployment import DeploymentResolver, deployment_mode
from lib.runtime import SUPPORTED_RUNTIMES, get_runtime_adapter


@dataclass(frozen=True, slots=True)
class ValidationError:
    """A single configuration validation error."""

    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.field}: {self.message}"


def validate_config(config: dict[str, Any]) -> list[ValidationError]:
    """Validate project configuration."""

    errors: list[ValidationError] = []

    errors.extend(_validate_deployment_mode(config))
    errors.extend(_validate_runtime(config))

    try:
        resolver = DeploymentResolver(config)
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(
            ValidationError(
                "models",
                str(exc),
            )
        )
        return errors

    errors.extend(_validate_features(config, resolver))

    return errors


# ---------------------------------------------------------------------------


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
        errors.append(
            ValidationError(
                "runtime.engine",
                f"Unsupported engine '{engine}'. Supported: {supported}",
            )
        )

    port = runtime.get("port")

    if port is None:
        errors.append(
            ValidationError(
                "runtime.port",
                "Missing 'port'",
            )
        )

    elif not isinstance(port, int) or not (1 <= port <= 65535):
        errors.append(
            ValidationError(
                "runtime.port",
                f"Invalid port '{port}'. Must be between 1 and 65535.",
            )
        )

    return errors


def _validate_deployment_mode(config: dict[str, Any]) -> list[ValidationError]:
    errors: list[ValidationError] = []

    raw_mode = str(config.get("deployment", {}).get("mode", "single")).strip().lower()
    normalized = deployment_mode(config)

    if raw_mode and raw_mode != normalized:
        errors.append(
            ValidationError(
                "deployment.mode",
                "Unsupported mode. Supported: single, multi.",
            )
        )

    return errors


def _validate_features(
    config: dict[str, Any],
    resolver: DeploymentResolver,
) -> list[ValidationError]:
    """Validate enabled features."""

    errors: list[ValidationError] = []

    engine = config["runtime"]["engine"]
    features = config.get("features", {})

    runtime_caps = None
    if engine in SUPPORTED_RUNTIMES:
        runtime_caps = get_runtime_adapter(engine).capabilities()

    deployments = [
        resolver.resolve(alias)
        for alias in resolver.aliases()
    ]

    # ------------------------------------------------------------------ #
    # Tool Calling
    # ------------------------------------------------------------------ #

    tool_calling = features.get("tool_calling", {})

    if tool_calling.get("enabled", False):

        if not tool_calling.get("parser"):
            errors.append(
                ValidationError(
                    "features.tool_calling.parser",
                    "Parser is required when tool calling is enabled.",
                )
            )

        if runtime_caps and not runtime_caps.tool_calling:
            errors.append(
                ValidationError(
                    "features.tool_calling",
                    f"Runtime '{engine}' does not support tool calling.",
                )
            )

        for resolved in deployments:
            if not resolved.metadata.supports_tool_calling:
                errors.append(
                    ValidationError(
                        "features.tool_calling",
                        f"Deployment '{resolved.deployment.alias}' does not support tool calling.",
                    )
                )

    # ------------------------------------------------------------------ #
    # Vision
    # ------------------------------------------------------------------ #

    vision = features.get("vision", {})

    if vision.get("enabled", False):

        if runtime_caps and not runtime_caps.vision:
            errors.append(
                ValidationError(
                    "features.vision",
                    f"Runtime '{engine}' does not support vision.",
                )
            )

        for resolved in deployments:
            if not resolved.metadata.supports_vision:
                errors.append(
                    ValidationError(
                        "features.vision",
                        f"Deployment '{resolved.deployment.alias}' does not support vision.",
                    )
                )

    # ------------------------------------------------------------------ #
    # Reasoning
    # ------------------------------------------------------------------ #

    reasoning = features.get("reasoning", {})

    if reasoning.get("enabled", False):

        for resolved in deployments:
            if not resolved.metadata.supports_reasoning:
                errors.append(
                    ValidationError(
                        "features.reasoning",
                        f"Deployment '{resolved.deployment.alias}' does not support reasoning.",
                    )
                )

    return errors