"""Module for Pipeline client API."""

import logging

from pathlib import PurePosixPath, PureWindowsPath

from ..base.clients import Client
from .models import Pipeline, PipelineCollection, PipelineConfiguration, PipelineConfigurationRepository, PipelineCreate

# Get a logger for this module
logger = logging.getLogger(__name__)


class PipelineClient(Client):
    """Represent a client to Pipelines API in Azure DevOps."""

    def get(self, id: int) -> Pipeline:
        """Get a pipeline by ID."""
        return self._get_resource(str(id), Pipeline)

    def list(self) -> PipelineCollection:
        """List all pipelines available in a project."""
        return self._get_resource("", PipelineCollection)

    def create(
        self, name: str, folder: str | PureWindowsPath, yaml_path: str | PurePosixPath, yaml_repository_id: str
    ) -> Pipeline:
        """Create a new pipeline in a project."""
        logger.info("Creating pipeline '%s/%s'...", folder, name)
        _folder = folder if isinstance(folder, PureWindowsPath) else PureWindowsPath(folder)
        _yaml_path = yaml_path if isinstance(yaml_path, PurePosixPath) else PurePosixPath(yaml_path)
        request_body = PipelineCreate(
            name=name,
            folder=_folder,
            configuration=PipelineConfiguration(
                path=_yaml_path,
                repository=PipelineConfigurationRepository(id=yaml_repository_id),
            ),
        )
        logger.debug("Post request body: %s", request_body.model_dump(mode="json"))
        return self._post_resource("", Pipeline, request_body.model_dump(mode="json"))
