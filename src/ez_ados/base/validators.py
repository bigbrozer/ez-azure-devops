"""Field validators for models."""

from pathlib import PurePosixPath, PureWindowsPath


def posix_path(value: str | PurePosixPath) -> PurePosixPath:
    """Validate the provided path is POSIX compatible."""
    if isinstance(value, PurePosixPath):
        return value
    elif isinstance(value, str):
        return PurePosixPath(value)
    else:
        raise ValueError("Cannot serialize to a path object !")


def windows_path(value: str | PureWindowsPath) -> PureWindowsPath:
    """Validate the provided path is Windows compatible."""
    if isinstance(value, PureWindowsPath):
        return value
    elif isinstance(value, str):
        return PureWindowsPath(value)
    else:
        raise ValueError("Cannot serialize to a path object !")


def git_branch_name(value: str) -> str:
    """Validate the git branch name and return the short version (without /refs/heads)."""
    return value.replace("refs/heads/", "")
