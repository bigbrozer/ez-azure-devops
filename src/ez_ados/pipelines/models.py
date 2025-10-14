"""Models for the Pipelines Azure DevOps API endpoint."""

from pathlib import PurePosixPath, PureWindowsPath
from typing import Annotated, Literal, Self

from pydantic import BeforeValidator, Field, HttpUrl

from ..base import validators
from ..base.models import BaseCollection, JSONModel
from .enums import ConfigurationType


class Pipeline(JSONModel):
    """Represents a pipeline resource."""

    id: int
    revision: int
    name: str
    folder: Annotated[PureWindowsPath, BeforeValidator(validators.windows_path)]
    url: HttpUrl


class PipelineConfigurationRepository(JSONModel):
    """Represents a pipeline configuration repository."""

    id: str
    type: Literal["azureReposGit"] = "azureReposGit"


class PipelineConfiguration(JSONModel):
    """Represents configuration of a pipeline resource."""

    path: Annotated[PurePosixPath, BeforeValidator(validators.posix_path)]
    type: Annotated[
        ConfigurationType, Field(default=ConfigurationType.yaml), BeforeValidator(ConfigurationType.validate)
    ] = ConfigurationType.yaml
    repository: PipelineConfigurationRepository


class PipelineDefinition(Pipeline):
    """Represents a pipeline definiton."""

    configuration: PipelineConfiguration


class PipelineCreate(JSONModel):
    """Represents a request to create a pipeline resource."""

    name: str
    folder: Annotated[PureWindowsPath, BeforeValidator(validators.windows_path)]
    configuration: PipelineConfiguration


class PipelineCollection(BaseCollection[Pipeline]):
    """Represents a collection of pipeline resources."""

    def startswith(self, pattern: str) -> Self:
        """Filter pipelines that have a name starting with `pattern`."""

        def _filter(p: Pipeline) -> bool:
            return p.name.startswith(pattern)

        filtered_results = list(filter(_filter, self))
        return type(self)(count=len(filtered_results), value=filtered_results)

    def from_folder(self, pattern: str) -> Self:
        """Filter pipelines that are contained in a folder."""

        def _filter(p: Pipeline) -> bool:
            return p.folder.match(pattern)

        filtered_results = list(filter(_filter, self))
        return type(self)(count=len(filtered_results), value=filtered_results)
