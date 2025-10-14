"""Logging module."""

import logging

from rich.logging import RichHandler

from ez_ados.core import console


class DebugFilter(logging.Filter):
    """Filter out non DEBUG levels."""

    def filter(self, record):
        """Filter out all non-DEBUG levels."""
        return True if record.levelname == "DEBUG" else False


# Handler for console output
CONSOLE_HANDLER = RichHandler(level=logging.INFO, console=console, show_time=False, show_path=False, markup=True)

# Handler for debug output
DEBUG_HANDLER = RichHandler(level=logging.DEBUG, console=console, show_time=False, rich_tracebacks=True, markup=True)


def get_root_logger() -> logging.Logger:
    """Return the application root logger."""
    DEBUG_HANDLER.addFilter(DebugFilter())

    root_logger = logging.getLogger("ez_ados")
    root_logger.addHandler(CONSOLE_HANDLER)
    root_logger.addHandler(DEBUG_HANDLER)

    return root_logger
