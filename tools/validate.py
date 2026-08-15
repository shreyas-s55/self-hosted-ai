#!/usr/bin/env python3
"""Validate project configuration."""

import sys

from lib.config_loader import load_config
from lib.validator import validate_config


def main() -> None:
    config = load_config()
    errors = validate_config(config)

    if errors:
        print("Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("Configuration is valid.")


if __name__ == "__main__":
    main()
