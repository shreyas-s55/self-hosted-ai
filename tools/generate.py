#!/usr/bin/env python3
"""Generate deployment artifacts from configuration."""

from pathlib import Path

from lib.config_loader import load_config
from lib.compose_generator import generate_compose, generate_env


def main() -> None:
    config = load_config()
    deploy_dir = Path("deploy")

    generate_env(config, deploy_dir / ".env")
    print("Generated deploy/.env")

    generate_compose(config, deploy_dir / "compose.generated.yaml")
    print("Generated deploy/compose.generated.yaml")


if __name__ == "__main__":
    main()
