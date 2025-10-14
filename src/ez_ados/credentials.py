"""Module for classes that provide multiple credentials to authenticate on the API."""

import logging

from azure.identity import ClientSecretCredential, DefaultAzureCredential

# Get a logger for this module
logger = logging.getLogger(__name__)

# Scope for Azure DevOps
SCOPE = "499b84ac-1321-427f-aa17-267ca6975798"


class TokenCredential:
    """Base class for token based credentials."""

    def get_token(self):
        """Return a token."""
        raise NotImplementedError("Missing method implementation")


class AccessTokenCredential(TokenCredential):
    """Class that manage authentication through an access token."""

    def __init__(self, token: str):
        """Init a new access token credential."""
        logger.debug("Azure DevOps: using provided token to authenticate")
        self.token = token

    def get_token(self):
        """Return a token."""
        return self.token


class AzureCredential(TokenCredential):
    """Class that auto detect best authentication method on Azure."""

    def __init__(self):
        """Init a new default azure credential."""
        self.credentials = DefaultAzureCredential()

    def get_token(self):
        """Return a token."""
        return self.credentials.get_token(SCOPE).token


class ServicePrincipalCredential(TokenCredential):
    """Class that authenticate using a service principal."""

    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        """Init a new service principal credential."""
        self.credentials = ClientSecretCredential(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id)

    def get_token(self):
        """Return a token."""
        return self.credentials.get_token(SCOPE).token


__all__ = [
    "AccessTokenCredential",
    "AzureCredential",
    "ServicePrincipalCredential",
    "TokenCredential",
]
