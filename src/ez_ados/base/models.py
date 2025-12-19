"""Module for base class models."""

from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


class JSONModel(BaseModel):
    """Base class for a model serializable to JSON."""

    model_config = ConfigDict(
        serialize_by_alias=True,
        validate_by_name=True,
        validate_by_alias=True,
    )


class BaseCollection[T](JSONModel):
    """Base class for a collection of resources in Azure DevOps."""

    value: Annotated[list[T], Field(default=[])] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def count(self) -> int:
        """Return the number of items in this collection."""
        return len(self.value)

    def append(self, element: T):
        """Append an element to the collection."""
        self.value.append(element)

    def __iter__(self):
        """Return an iterator on all values."""
        return self.value.__iter__()

    def __getitem__(self, index: int):
        """Return a value from given index."""
        return self.value[index]
