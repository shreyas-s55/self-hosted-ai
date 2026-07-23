#!/usr/bin/env python3
"""Generate deployment artifacts from configuration."""

import argparse

from pathlib import Path

from lib.config_loader import load_config
from lib.compose_generator import generate_compose, generate_env


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deployment artifacts from configuration.",
    )

    parser.add_argument(
        "--mode",
        choices=("single", "multi"),
        default=None,
        help="Deployment mode. Defaults to single.",
    )

    parser.add_argument(
        "--profile",
        default=None,
        help="Deployment profile (e.g. single, multi).",
    )

    parser.add_argument(
        "--pin-gpus",
        action="store_true",
        default=False,
        help="Pin each multi-mode runtime container to a dedicated GPU (CUDA_VISIBLE_DEVICES). "
             "Use on multi-GPU instances (e.g. g6.12xlarge).",
    )

    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    config = load_config()

    profile = str(args.profile).strip().lower() if args.profile else ""

    if args.mode:
        config["deployment"] = {"mode": args.mode}
    elif profile:
        config["deployment"] = {"mode": profile}

    if args.pin_gpus:
        config.setdefault("deployment", {})["pin_gpus"] = True

    deploy_dir = Path("deploy")

    generate_env(config, deploy_dir / ".env")
    print("Generated deploy/.env")

    generate_compose(config, deploy_dir / "compose.generated.yaml")
    print("Generated deploy/compose.generated.yaml")


if __name__ == "__main__":
    main()
