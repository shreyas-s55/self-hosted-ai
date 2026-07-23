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
    deployments_cfg = config.get("deployments")

    if deployments_cfg is not None:
        return _load_deployments(config, deployments_cfg)

    models_cfg = config.get("models")

    if models_cfg is None:
        raise ValueError(
            "Missing 'models' section in configuration. "
            "Alternatively, configure 'deployments'."
        )

    return _load_legacy_models(config, models_cfg)


def _load_legacy_models(
    config: dict[str, Any],
    models_cfg: Any,
) -> dict[str, DeploymentModel]:
    if not isinstance(models_cfg, dict):
        raise ValueError("'models' must be a mapping.")

    runtime_engine = str(config.get("runtime", {}).get("engine", "")) or None

    deployment_models: dict[str, DeploymentModel] = {}

    for index, (alias, model_cfg) in enumerate(models_cfg.items()):
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
            runtime=runtime_engine,
            default=index == 0,
        )

    return deployment_models


def _load_deployments(
    config: dict[str, Any],
    deployments_cfg: Any,
) -> dict[str, DeploymentModel]:
    if not isinstance(deployments_cfg, dict):
        raise ValueError("'deployments' must be a mapping.")

    runtime_engine = str(config.get("runtime", {}).get("engine", "")) or None

    deployment_models: dict[str, DeploymentModel] = {}
    default_count = 0

    for alias, dep_cfg in deployments_cfg.items():
        if not isinstance(dep_cfg, dict):
            raise ValueError(
                f"Configuration for deployment '{alias}' must be a mapping."
            )

        source = dep_cfg.get("model") or dep_cfg.get("source")
        if not source:
            raise ValueError(
                f"Deployment '{alias}' is missing required field 'model' (or 'source')."
            )

        parameters = dep_cfg.get("parameters", {})
        if not isinstance(parameters, dict):
            raise ValueError(
                f"'parameters' for deployment '{alias}' must be a mapping."
            )

        deployment_runtime = dep_cfg.get("runtime") or runtime_engine

        is_default = bool(dep_cfg.get("default", False))
        if is_default:
            default_count += 1

        deployment_models[alias] = DeploymentModel(
            alias=alias,
            source=str(source),
            parameters=parameters,
            runtime=str(deployment_runtime) if deployment_runtime else None,
            default=is_default,
        )

    if not deployment_models:
        raise ValueError("'deployments' must define at least one deployment.")

    if default_count > 1:
        raise ValueError("Only one deployment can set default=true.")

    if default_count == 0:
        first_alias = next(iter(deployment_models))
        first = deployment_models[first_alias]
        deployment_models[first_alias] = DeploymentModel(
            alias=first.alias,
            source=first.source,
            parameters=first.parameters,
            runtime=first.runtime,
            default=True,
        )

    return deployment_models