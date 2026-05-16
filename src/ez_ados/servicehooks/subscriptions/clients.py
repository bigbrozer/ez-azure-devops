"""Module for Service Hooks' Subscriptions client API."""

import logging

from ...base.clients import Client
from .models import HookSubscription, HookSubscriptionCollection, HookSubscriptionCreate

# Get a logger for this module
logger = logging.getLogger(__name__)


class HookSubscriptionClient(Client):
    """Represent a client to Git repository API in Azure DevOps."""

    def get(self, id: str) -> HookSubscription:
        """Fetch a single Service Hook's subscription."""
        logger.info("Fetching details for hook subscription with id '%s'...", id)
        resource = self._get_resource(id, HookSubscription)
        logger.debug(resource)
        return resource

    def list(self) -> HookSubscriptionCollection:
        """List all Service Hook's available in organization."""
        return self._get_resource("", HookSubscriptionCollection)

    def delete(self, id: str) -> None:
        """Delete a single Service Hook's subscription."""
        logger.info("Deleting service hook subscription with id=%s...", id)
        self._delete_resource(id)

    def create(self, definition: HookSubscriptionCreate) -> HookSubscription:
        """Create a new Service Hook's subscription."""
        logger.debug("Create new hook subscription: %s", definition)
        return self._post_resource("", HookSubscription, definition.model_dump(exclude_none=True))
