"""Module for Git Pull Request Threads models."""

from datetime import datetime
from typing import Annotated, Any

from pydantic import BeforeValidator, Field

from ...base.models import BaseCollection, JSONModel
from ...core.models import Properties
from .enums import CommentTypeEnum, ThreadStatusEnum


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
