"""Configuration validator."""

from dataclasses import dataclass
from typing import Any

from lib.runtime import SUPPORTED_RUNTIMES


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

    # Runtime section
    runtime = config.get("runtime")
    if runtime is None:
        errors.append(ValidationError("runtime", "Missing 'runtime' section"))
    else:
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

    # Model section
    model = config.get("model")
    if model is None:
        errors.append(ValidationError("model", "Missing 'model' section"))
    else:
        if not model.get("name"):
            errors.append(ValidationError("model.name", "Missing 'name'"))

    # Features section
    features = config.get("features", {})
    tool_calling = features.get("tool_calling", {})
    if tool_calling.get("enabled", False):
        if not tool_calling.get("parser"):
            errors.append(ValidationError(
                "features.tool_calling.parser",
                "Parser is required when tool calling is enabled",
            ))

    return errors
