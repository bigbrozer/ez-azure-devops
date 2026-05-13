"""Module for Policy Configuration client API."""

import logging

from ...base.clients import Client
from ...constants import BUILD_POLICY_TYPE_ID
from .models import PolicyConfiguration, PolicyConfigurationCollection, PolicyConfigurationPayload

# Get a logger for this module
logger = logging.getLogger(__name__)


class PolicyConfigurationClient(Client):
    """Represent a client to Policy Configuration API in Azure DevOps."""

    def delete_policy(self, id: int) -> int:
        """Delete a policy configuration by ID."""
        logger.info("Deleting policy configuration ID %s...", id)
        return self._delete_resource(str(id))

    def create_build_policy(self, definition: PolicyConfigurationPayload) -> PolicyConfiguration:
        """Create a new build policy for a branch."""
        logger.debug("Creating a new build policy: %s", definition)
        return self._post_resource("", PolicyConfiguration, definition.model_dump(mode="json"))

    def update_build_policy(self, id: int, definition: PolicyConfigurationPayload) -> PolicyConfiguration:
        """Update an existing build policy by ID for a branch."""
        logger.debug("Updating build policy with id=%d: %s", id, definition)
        return self._put_resource(str(id), PolicyConfiguration, definition.model_dump(mode="json"))


class GitPolicyConfigurationClient(Client):
    """Client to the Git Repository Policy Configuration API in Azure DevOps."""

    def get_policies_for_ref(
        self, repository_id: str, ref_name: str, policy_type: str
    ) -> PolicyConfigurationCollection:
        """Get all policies for a branch of a repository."""
        response = self._raise_for_status(
            self._client.get("", params={"repositoryId": repository_id, "refName": ref_name, "policyType": policy_type})
        )
        logger.debug("Request URL: %s\nResponse: %s", response.url, response.content)
        return PolicyConfigurationCollection.model_validate(response.json())

    def get_build_policies_for_ref(self, repository_id: str, ref_name: str) -> PolicyConfigurationCollection:
        """Get all build policies for a branch of a repository."""
        return self.get_policies_for_ref(
            repository_id=repository_id,
            ref_name=ref_name,
            policy_type=BUILD_POLICY_TYPE_ID,
        )
