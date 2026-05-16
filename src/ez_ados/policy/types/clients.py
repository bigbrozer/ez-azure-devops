"""Module for Policy Teypes client API."""

import logging

from ...base.clients import Client
from .models import PolicyType, PolicyTypeCollection

# Get a logger for this module
logger = logging.getLogger(__name__)


class PolicyTypeClient(Client):
    """Represent a client to Policy Types API in Azure DevOps."""

    def list(self) -> PolicyTypeCollection:
        """List all policy types available in a project."""
        return self._get_resource("", PolicyTypeCollection)

    def get(self, id: str) -> PolicyType:
        """Get a policy type by ID."""
        return self._get_resource(id, PolicyType)
