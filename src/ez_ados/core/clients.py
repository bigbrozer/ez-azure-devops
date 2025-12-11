"""Module for Core clients API."""

from ..base.clients import Client
from .models import Project


class ProjectClient(Client):
    """Represent a client to Project API in Azure DevOps."""

    def get(self, name: str) -> Project:
        """Get a single project resource."""
        return Project.model_validate(self._client.get(name).raise_for_status().json())
