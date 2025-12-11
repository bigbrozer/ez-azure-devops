"""Module for Builds client API."""

import logging

from ..base.clients import Client
from ..git.models import GitRepository
from .models import (
    BuildDefinition,
    BuildDefinitionCollection,
    BuildDefinitionCreate,
)

# Get a logger for this module
logger = logging.getLogger(__name__)


class BuildClient(Client):
    """Represent a client to Builds API in Azure DevOps."""

    def get_build_definition(self, id: str) -> BuildDefinition:
        """Get a build definition by ID."""
        logger.debug("Getting build definition id=%d", id)
        response = BuildDefinition.model_validate(self._client.get(f"/definitions/{id}").raise_for_status().json())
        logger.debug("Build definition id=%s specs: %s", id, response)
        return response

    def list_build_definitions(self, repository: GitRepository | None = None) -> BuildDefinitionCollection:
        """List all build definitions available in a project."""
        _query_params: dict[str, str] = {}

        # Build query params
        if isinstance(repository, GitRepository):
            _query_params["repositoryId"] = repository.id
            _query_params["repositoryType"] = "TfsGit"

        return BuildDefinitionCollection.model_validate(
            self._client.get("/definitions", params=_query_params).raise_for_status().json()
        )

    def create_build_definition(self, definition: BuildDefinitionCreate) -> BuildDefinition:
        """Create a new build definition in a project."""
        logger.debug(
            'Creating build definition "%s/%s": yaml_path="%s", yaml_repo_id="%s"',
            definition.path,
            definition.name,
            definition.process.yaml_filename,
            definition.repository.id,
        )

        logger.debug("Post request body: %s", definition.model_dump(mode="json"))
        response = self._client.post("/definitions", json=definition.model_dump(mode="json")).raise_for_status()
        serialized_response = BuildDefinition.model_validate(response.json())

        logger.debug("Build definition resource created: %s", serialized_response)
        return serialized_response

    def delete_build_definition(self, id: int) -> int:
        """Delete a build definition resource."""
        response = self._client.delete(f"/definitions/{id}").raise_for_status()
        return response.status_code
