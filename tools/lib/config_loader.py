"""Configuration loader."""

from pathlib import Path
from typing import Any

import yaml


def load_config(path: Path | str = "config/config.yaml") -> dict[str, Any]:
    """Load the project configuration from a YAML file.

    Args:
        path: Path to the configuration YAML file.

    Returns:
        The parsed configuration dictionary.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with open(path) as f:
        return yaml.safe_load(f)
