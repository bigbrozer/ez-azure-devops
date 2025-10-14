"""Module for Policy Teypes client API."""

import logging

from ...base.clients import Client
from ...base.error_handlers import retry_on_http_error
from .models import PolicyType, PolicyTypeCollection

# Get a logger for this module
logger = logging.getLogger(__name__)


class PolicyTypeClient(Client):
    """Represent a client to Policy Types API in Azure DevOps."""

    @retry_on_http_error
    def list(self) -> PolicyTypeCollection:
        """List all policy types available in a project."""
        return PolicyTypeCollection.model_validate(self._client.get("").raise_for_status().json())

    @retry_on_http_error
    def get(self, id: str) -> PolicyType:
        """Get a policy type by ID.."""
        return PolicyType.model_validate(self._client.get(id).raise_for_status().json())
