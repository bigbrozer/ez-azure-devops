"""Models for policy types schemas in Azure DevOps."""

from typing import Annotated

from pydantic import Field, HttpUrl

from ...base.models import BaseCollection, JSONModel


class PolicyType(JSONModel):
    """Represent a policy type configuration."""

    id: str
    url: HttpUrl
    display_name: Annotated[str, Field(alias="displayName")]
    description: str | None = None


class PolicyTypeCollection(BaseCollection[PolicyType]):
    """Represent a collection of policy types."""
