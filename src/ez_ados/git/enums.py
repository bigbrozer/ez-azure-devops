"""Enumerations for Git types."""

from ..base.enums import StrIntEnum


class RecursionType(StrIntEnum):
    """Enum for available recursion modes."""

    none = 0
    oneLevel = 1
    oneLevelPlusNestedEmptyFolders = 4
    full = 120


class GitObjectType(StrIntEnum):
    """Enum for available type of objects in git."""

    bad = 0
    commit = 1
    tree = 2
    blob = 3
    tag = 4
    ext2 = 5
    ofsDelta = 6
    refDelta = 7
