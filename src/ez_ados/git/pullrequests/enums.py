"""Enumerations for Git Pull Requests types."""

from ...base.enums import StrIntEnum


class CommentTypeEnum(StrIntEnum):
    """Enum for available pull request thread comments."""

    unknown = 0
    text = 1
    codeChange = 2
    system = 3


class ThreadStatusEnum(StrIntEnum):
    """Enum for available pull request thread statuses."""

    unknown = 0
    active = 1
    fixed = 2
    wontFix = 3
    closed = 4
    byDesign = 5
    pending = 6


class VoteEnum(StrIntEnum):
    """Enum for available pull request reviewer votes."""

    rejected = -10
    waitingForAuthor = -5
    noVote = 0
    approvedWithSuggestions = 5
    approved = 10
