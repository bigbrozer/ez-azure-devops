"""Models for the Identity Management Service (IMS) API."""

from typing import Annotated

from pydantic import Field

from ..base.models import BaseCollection, JSONModel


class Identity(JSONModel):
    """Represent an Azure DevOps identity."""

    id: str
    provider_display_name: Annotated[str | None, Field(alias="providerDisplayName", default=None)] = None
    is_active: Annotated[bool | None, Field(alias="isActive", default=None)] = None
    descriptor: str | None = None
    subject_descriptor: Annotated[str | None, Field(alias="subjectDescriptor", default=None)] = None


class IdentityCollection(BaseCollection[Identity]):
    """Represent a collection of identities."""
