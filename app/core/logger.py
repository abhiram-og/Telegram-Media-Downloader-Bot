"""Centralized logging configuration."""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Create and return a configured logger.

    Sets up a logger with a consistent format and console output.
    If the logger already has handlers, returns it as-is to avoid
    duplicate log entries.

    Args:
        name: The name for the logger, typically ``__name__``.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
