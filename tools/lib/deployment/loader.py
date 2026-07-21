"""Deployment configuration loader.

This module converts the raw deployment configuration into strongly typed
deployment objects.

The deployment layer represents what THIS deployment exposes, independent
of the platform model catalog.
"""

from typing import Any

from .model import DeploymentModel


def load_models(config: dict[str, Any]) -> dict[str, DeploymentModel]:
    """Load deployment models from the project configuration.

    Args:
        config: Parsed project configuration.

    Returns:
        Dictionary mapping deployment aliases to DeploymentModel objects.

    Raises:
        ValueError:
            If the configuration does not contain a valid ``models`` section.
    """
    models_cfg = config.get("models")

    if models_cfg is None:
        raise ValueError("Missing 'models' section in configuration.")

    if not isinstance(models_cfg, dict):
        raise ValueError("'models' must be a mapping.")

    deployment_models: dict[str, DeploymentModel] = {}

    for alias, model_cfg in models_cfg.items():
        if not isinstance(model_cfg, dict):
            raise ValueError(
                f"Configuration for deployment model '{alias}' must be a mapping."
            )

        source = model_cfg.get("source")
        if not source:
            raise ValueError(
                f"Deployment model '{alias}' is missing required field 'source'."
            )

        parameters = model_cfg.get("parameters", {})

        if not isinstance(parameters, dict):
            raise ValueError(
                f"'parameters' for deployment model '{alias}' must be a mapping."
            )

        deployment_models[alias] = DeploymentModel(
            alias=alias,
            source=source,
            parameters=parameters,
        )

    return deployment_models