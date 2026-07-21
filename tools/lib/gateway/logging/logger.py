"""Gateway logger."""

import logging
import sys

from .formatter import JsonFormatter


_LOGGER = None


def get_logger() -> logging.Logger:
    """Return the singleton gateway logger."""

    global _LOGGER

    if _LOGGER is not None:
        return _LOGGER

    logger = logging.getLogger("self-hosted-ai.gateway")

    logger.setLevel(logging.INFO)

    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger.handlers.clear()
    logger.addHandler(handler)

    _LOGGER = logger

    return logger