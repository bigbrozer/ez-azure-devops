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
        resource = HookSubscription.model_validate(self._client.get(id).raise_for_status().json())
        logger.debug(resource)
        return resource

    def list(self) -> HookSubscriptionCollection:
        """List all Service Hook's available in organization."""
        return HookSubscriptionCollection.model_validate(self._client.get("").raise_for_status().json())

    def delete(self, id: str) -> None:
        """Fetch a single Service Hook's subscription."""
        logger.info("Deleting service hook subscription with id=%s...", id)
        self._client.delete(id).raise_for_status()

    def create(self, definition: HookSubscriptionCreate) -> HookSubscription:
        """Create a new Service Hook's subscription."""
        resource = HookSubscriptionCreate.model_validate(definition)
        logger.debug("Create new hook subscription: %s", definition)

        post_request = self._client.post("", json=resource.model_dump(exclude_none=True))
        post_request.raise_for_status()
        new_resource = post_request.json()
        logger.debug("Create new hook subscription status code: %s", post_request.status_code)
        logger.debug("Create new hook subscription response: %s", post_request.content)

        return HookSubscription.model_validate(new_resource)
