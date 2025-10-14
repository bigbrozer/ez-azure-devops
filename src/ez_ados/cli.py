"""CLI entrypoint."""

import logging

import click

from ez_ados.core import console
from ez_ados.logs import get_root_logger
from ez_ados.version import __version__

# Get a logger for this module
logger = logging.getLogger(__name__)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug mode.")
def entrypoint(debug):
    """Python interface to interact with Azure DevOps API."""
    root_logger = get_root_logger()

    if debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)

    logger.debug("Starting ez_ados, v%s.", __version__, extra={"highlighter": None})
    logger.debug("DEBUG mode is on.")


@entrypoint.command()  # noqa
def version():
    """Show program version then exit."""
    console.print(f"ez_ados v{__version__}")


if __name__ == "__main__":  # pragma: no cover
    entrypoint()
