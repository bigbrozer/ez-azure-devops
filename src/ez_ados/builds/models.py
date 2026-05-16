"""Models for the Builds Azure DevOps API endpoint."""

from pathlib import PurePosixPath, PureWindowsPath
from typing import Annotated, Literal, Self

from pydantic import BeforeValidator, Field, HttpUrl, computed_field

from ..base import validators
from ..base.models import BaseCollection, JSONModel
from ..core.models import Properties


class BuildProcess(JSONModel):
    """Represents a build process resource."""

    type: int = 2
    yaml_filename: Annotated[PurePosixPath, BeforeValidator(validators.posix_path), Field(alias="yamlFilename")]


class BuildRepository(JSONModel):
    """Represents a repository used to create a build definition."""

    id: str
    type: Literal["TfsGit"] = "TfsGit"
    default_branch: Annotated[str | None, Field(alias="defaultBranch", default=None)] = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def default_branch_name(self) -> str | None:
        """Return the short name for the default branch (without refs/heads/)."""
        if self.default_branch:
            return validators.git_branch_name(self.default_branch)
        else:
            return None


class BuildDefinitionSummary(JSONModel):
    """Summary of a build definition as returned by list endpoints."""

    id: int
    revision: int
    name: str
    path: Annotated[PureWindowsPath, BeforeValidator(validators.windows_path)]
    url: HttpUrl
    properties: dict[str, Properties] | None = None


class BuildDefinitionCreate(JSONModel):
    """Represents a request to create a new build definition."""

    name: str
    path: Annotated[PureWindowsPath, BeforeValidator(validators.windows_path)]
    type: Literal["xaml", "build"] = "build"
    process: BuildProcess
    repository: BuildRepository
    properties: dict[str, Properties] | None = None


class BuildDefinition(BuildDefinitionSummary):
    """Represents a build definition resource."""

    process: BuildProcess
    repository: BuildRepository

    @computed_field  # type: ignore[prop-decorator]
    @property
    def fullname(self) -> PurePosixPath:
        """Return the fullname including path."""
        return PurePosixPath(self.path.joinpath(self.name))


class BuildDefinitionCollection(BaseCollection[BuildDefinitionSummary]):
    """Represents a collection of build definition resources."""

    def startswith(self, pattern: str) -> Self:
        """Filter build definitions that have a name starting with `pattern`."""
        return self._filtered(lambda p: p.name.startswith(pattern))

    def from_folder(self, pattern: str) -> Self:
        """Filter build definitions that are contained in a folder."""
        return self._filtered(lambda p: p.path.match(pattern))

    def get(self, name: str) -> BuildDefinitionSummary | None:
        """Get a build definition by `name` or None if not found."""
        for item in self:
            if item.name == name:
                return item
        return None
