"""Module for Git Pull Request Threads models."""

from datetime import datetime
from typing import Annotated, Any

from pydantic import BeforeValidator, Field

from ...base.models import BaseCollection, JSONModel
from ...core.models import Properties
from .enums import CommentTypeEnum, ThreadStatusEnum, VoteEnum


class PullRequestThreadCommentCreate(JSONModel):
    """Model for creating a new comment on a pull request thread."""

    content: str
    comment_type: Annotated[CommentTypeEnum, BeforeValidator(CommentTypeEnum.validate), Field(alias="commentType")] = (
        CommentTypeEnum.system
    )


class PullRequestThreadComment(JSONModel):
    """Model for a comment on a pull request thread."""

    id: int
    parent_comment_id: Annotated[int, Field(alias="parentCommentId")]
    published_date: Annotated[datetime, Field(alias="publishedDate")]
    last_updated_date: Annotated[datetime, Field(alias="lastUpdatedDate")]
    last_content_updated_date: Annotated[datetime, Field(alias="lastContentUpdatedDate")]
    content: str | None = None
    comment_type: Annotated[CommentTypeEnum, BeforeValidator(CommentTypeEnum.validate), Field(alias="commentType")]


class PullRequestThreadCreate(JSONModel):
    """Model for creating a new pull request thread."""

    comments: list[PullRequestThreadCommentCreate]
    status: Annotated[ThreadStatusEnum | None, BeforeValidator(ThreadStatusEnum.validate)] = None
    properties: dict[str, Any] = {}


class PullRequestThread(JSONModel):
    """Model for a pull request thread."""

    id: int
    published_date: Annotated[datetime, Field(alias="publishedDate")]
    last_updated_date: Annotated[datetime, Field(alias="lastUpdatedDate")]
    deleted: Annotated[bool, Field(alias="isDeleted")]
    comments: list[PullRequestThreadComment]
    properties: dict[str, Properties] | None = None


class PullRequestThreadCollection(BaseCollection[PullRequestThread]):
    """Represent a collection of git pull request threads reference."""


class IdentityRefWithVote(JSONModel):
    """Identity information including a vote on a pull request."""

    id: str
    display_name: Annotated[str | None, Field(alias="displayName", default=None)] = None
    unique_name: Annotated[str | None, Field(alias="uniqueName", default=None)] = None
    vote: Annotated[VoteEnum, BeforeValidator(VoteEnum.validate)] = VoteEnum.noVote
    has_declined: Annotated[bool | None, Field(alias="hasDeclined", default=None)] = None
    is_flagged: Annotated[bool | None, Field(alias="isFlagged", default=None)] = None
    is_required: Annotated[bool | None, Field(alias="isRequired", default=None)] = None
    reviewer_url: Annotated[str | None, Field(alias="reviewerUrl", default=None)] = None


class IdentityRefWithVoteCollection(BaseCollection[IdentityRefWithVote]):
    """Represent a collection of pull request reviewers."""


class IdentityRefCreate(JSONModel):
    """Model for adding a reviewer to a pull request."""

    id: str
    is_required: Annotated[bool | None, Field(alias="isRequired", default=None)] = None
    vote: Annotated[VoteEnum | None, BeforeValidator(VoteEnum.validate), Field(default=None)] = None
