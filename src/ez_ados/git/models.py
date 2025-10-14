"""Models for the Git Azure DevOps API endpoint."""

from pathlib import PurePosixPath
from typing import Annotated, Literal, Self

from pydantic import BeforeValidator, Field, HttpUrl

from ..base import validators
from ..base.models import BaseCollection, JSONModel
from ..core.models import Project
from .enums import GitObjectType, RecursionType


class GitRepository(JSONModel):
    """Model for a git repository."""

    id: str
    name: str
    project: Project
    default_branch: Annotated[str, Field(alias="defaultBranch")]
    size: int
    remote_url: Annotated[HttpUrl, Field(alias="remoteUrl")]
    web_url: Annotated[HttpUrl, Field(alias="webUrl")]
    disabled: Annotated[bool, Field(alias="isDisabled")]
    maintenance: Annotated[bool, Field(alias="isInMaintenance")]


class GitRef(JSONModel):
    """Represent a reference (branch) in a git repository."""

    name: str
    object_id: str = Field(alias="objectId")
    locked: bool | None = Field(alias="isLocked", default=None)


class GitRefCollection(BaseCollection[GitRef]):
    """Represent a collection of git repository reference."""


class GitItemDescriptor(JSONModel):
    """Represent descriptors for files and folders inside a Git repository."""

    path: Annotated[PurePosixPath, BeforeValidator(validators.posix_path)]
    version: Annotated[str, BeforeValidator(validators.git_branch_name)]
    recursion_level: Annotated[
        RecursionType,
        Field(alias="recursionLevel", default=RecursionType.full),
        BeforeValidator(RecursionType.validate),
    ] = RecursionType.full
    version_options: Annotated[
        Literal["none", "previousChange", "firstParent"], Field(alias="versionOptions", default="none")
    ] = "none"
    version_type: Annotated[Literal["branch", "tag", "commit"], Field(alias="versionType", default="branch")] = "branch"


class GitItemsBatch(JSONModel):
    """Represent the body for Git items batch requests."""

    item_descriptors: Annotated[list[GitItemDescriptor], Field(alias="itemDescriptors")]
    include_content_metadata: Annotated[bool, Field(alias="includeContentMetadata", default=False)] = False
    include_links: Annotated[bool, Field(alias="includeLinks", default=False)] = False
    latest_processed_change: Annotated[bool, Field(alias="latestProcessedChange", default=False)] = False


class GitItem(JSONModel):
    """Represent a git item (files or folders)."""

    object_id: Annotated[str, Field(alias="objectId")]
    git_object_type: Annotated[GitObjectType, BeforeValidator(GitObjectType.validate), Field(alias="gitObjectType")]
    is_folder: Annotated[bool | None, Field(alias="isFolder", default=None)] = None
    is_symlink: Annotated[bool | None, Field(alias="isSymlink", default=None)] = None
    path: Annotated[PurePosixPath, BeforeValidator(validators.posix_path)]
    content: str | None = None


class GitItemCollection(BaseCollection[GitItem]):
    """Represent a collection of git item (files or folders)."""

    def match(self, pattern: str) -> Self:
        """Return a list of items which match a given pattern."""

        def _filter(i: GitItem) -> bool:
            return i.path.match(pattern)

        filtered_results = list(filter(_filter, self))
        return type(self)(count=len(filtered_results), value=filtered_results)
