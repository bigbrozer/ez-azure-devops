"""Models for the Core Azure DevOps API endpoint."""

from typing import Annotated, Any

from pydantic import Field

from ..base.models import JSONModel


class Project(JSONModel):
    """Model for a project."""

    id: str
    name: str


class Properties(JSONModel):
    """Model for properties attached to resources."""

    type: Annotated[str | None, Field(alias="$type", default=None)] = None
    value: Annotated[Any, Field(alias="$value")]
