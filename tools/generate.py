#!/usr/bin/env python3
"""Generate deployment artifacts from configuration."""

import copy
from pathlib import Path

from lib.config_loader import load_config
from lib.compose_generator import generate_compose, generate_env
from lib.models import MODEL_REGISTRY


def main() -> None:
    config = load_config()

    # Resolve a short model name (e.g. "qwen-chat") to the full HuggingFace
    # repo before generating artifacts. Full repos pass through unchanged,
    # keeping backward compatibility with existing configs.
    config = copy.deepcopy(config)
    config["model"]["name"] = MODEL_REGISTRY.resolve_repo(config["model"]["name"])

    deploy_dir = Path("deploy")

    generate_env(config, deploy_dir / ".env")
    print("Generated deploy/.env")

    generate_compose(config, deploy_dir / "compose.generated.yaml")
    print("Generated deploy/compose.generated.yaml")


if __name__ == "__main__":
    main()
