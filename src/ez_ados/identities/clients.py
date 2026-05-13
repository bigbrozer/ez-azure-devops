"""Clients for the Identity Management Service (IMS) API."""

import logging

from ..base.clients import Client
from .models import Identity, IdentityCollection

# Get a logger for this module
logger = logging.getLogger(__name__)


class IdentityClient(Client):
    """Client for interacting with the IMS Identities endpoint."""

    def search_by_email(self, email: str) -> IdentityCollection:
        """Search for identities by email address."""
        logger.info("Searching for identity by email '%s'", email)
        return self._get_resource(
            "/",
            IdentityCollection,
            searchFilter="General",
            filterValue=email,
            queryMembership="None",
        )

    def resolve_identities_by_email(self, emails: list[str]) -> list[Identity]:
        """Resolve multiple email addresses to identities."""
        resolved: list[Identity] = []
        unresolved: list[str] = []

        for email in emails:
            collection = self.search_by_email(email)
            if collection.count > 0:
                resolved.append(collection[0])
            else:
                unresolved.append(email)

        if unresolved:
            raise ValueError(f"Could not resolve identities for: {', '.join(unresolved)}")

        return resolved
