"""Module for Policy Configuration client API."""

import logging

from ...base.clients import Client
from .models import PolicyConfiguration, PolicyConfigurationCreate, PolicyConfigurationUpdate

# Get a logger for this module
logger = logging.getLogger(__name__)


class PolicyConfigurationClient(Client):
    """Represent a client to Policy Configuration API in Azure DevOps."""

    def delete_policy(self, id: int) -> int:
        """Delete a policy configuration by ID."""
        logger.info("Deleting policy configuration ID %s...", id)
        response = self._client.delete(str(id)).raise_for_status()
        return response.status_code

    def create_build_policy(self, definition: PolicyConfigurationCreate) -> PolicyConfiguration:
        """Create a new build policy for a branch."""
        logger.debug("Creating a new build policy: %s", definition)
        response = self._client.post("", json=definition.model_dump(mode="json")).raise_for_status()
        return PolicyConfiguration.model_validate(response.json())

    def update_build_policy(self, id: int, definition: PolicyConfigurationUpdate) -> PolicyConfiguration:
        """Update an existing build policy by ID for a branch."""
        logger.debug("Updating a new build policy with id=%d: %s", id, definition)
        response = self._client.put(f"{id}", json=definition.model_dump(mode="json")).raise_for_status()
        return PolicyConfiguration.model_validate(response.json())
