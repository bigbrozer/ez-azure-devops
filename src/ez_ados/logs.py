"""Logging module."""

import logging


def get_root_logger() -> logging.Logger:
    """Return the application root logger."""
    root_logger = logging.getLogger("ez_ados")
    return root_logger
