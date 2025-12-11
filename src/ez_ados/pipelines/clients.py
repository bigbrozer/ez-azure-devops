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
        return Pipeline.model_validate(self._client.get(str(id)).raise_for_status().json())

    def list(self) -> PipelineCollection:
        """List all pipelines available in a project."""
        return PipelineCollection.model_validate(self._client.get("").raise_for_status().json())

    def create(
        self, name: str, folder: str | PureWindowsPath, yaml_path: str | PurePosixPath, yaml_repository_id: str
    ) -> Pipeline:
        """Create a new pipeline in a project."""
        logger.info("Creating pipeline '%s/%s'...", folder, name)
        if not isinstance(folder, PureWindowsPath):
            _folder = PureWindowsPath(folder)
        else:
            _folder = folder

        if not isinstance(yaml_path, PurePosixPath):
            _yaml_path = PurePosixPath(yaml_path)
        else:
            _yaml_path = yaml_path

        request_body = PipelineCreate(
            name=name,
            folder=_folder,
            configuration=PipelineConfiguration(
                path=_yaml_path,
                repository=PipelineConfigurationRepository(id=yaml_repository_id),
            ),
        )
        logger.debug("Post request body: %s", request_body.model_dump(mode="json"))
        response = self._client.post("", json=request_body.model_dump(mode="json")).raise_for_status()
        return Pipeline.model_validate_json(response.content)
