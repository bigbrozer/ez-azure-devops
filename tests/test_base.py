"""Tests for the base module: models, enums, validators, and misc utilities."""

import logging

from pathlib import PurePosixPath, PureWindowsPath
from typing import Annotated

import pytest

from pydantic import Field

from ez_ados.base.enums import StrIntEnum
from ez_ados.base.models import BaseCollection, JSONModel
from ez_ados.base.validators import git_branch_name, posix_path, windows_path
from ez_ados.logs import get_root_logger
from ez_ados.version import __version__

# ---------------------------------------------------------------------------
# JSONModel
# ---------------------------------------------------------------------------


class _AliasedModel(JSONModel):
    """Concrete JSONModel with an aliased field for testing."""

    my_field: Annotated[str, Field(alias="myField")]


def test_jsonmodel_empty_dump():
    assert JSONModel().model_dump() == {}


def test_jsonmodel_validate_by_alias():
    m = _AliasedModel.model_validate({"myField": "hello"})
    assert m.my_field == "hello"


def test_jsonmodel_validate_by_name():
    m = _AliasedModel.model_validate({"my_field": "hello"})
    assert m.my_field == "hello"


def test_jsonmodel_serialize_by_alias():
    m = _AliasedModel(myField="world")
    assert m.model_dump(by_alias=True) == {"myField": "world"}


# ---------------------------------------------------------------------------
# BaseCollection
# ---------------------------------------------------------------------------


def test_basecollection_append_and_count():
    col: BaseCollection[str] = BaseCollection[str]()
    col.append("a")
    col.append("b")
    assert col.count == 2


def test_basecollection_iter():
    col: BaseCollection[str] = BaseCollection[str]()
    col.append("x")
    col.append("y")
    assert list(col) == ["x", "y"]


def test_basecollection_getitem():
    col: BaseCollection[str] = BaseCollection[str]()
    col.append("only")
    assert col[0] == "only"


def test_basecollection_filtered_keeps_matching():
    col: BaseCollection[str] = BaseCollection[str]()
    for v in ("foo", "bar", "foobar", "baz"):
        col.append(v)
    result = col._filtered(lambda v: v.startswith("foo"))
    assert result.count == 2
    assert list(result) == ["foo", "foobar"]


def test_basecollection_filtered_empty_when_nothing_matches():
    col: BaseCollection[str] = BaseCollection[str]()
    col.append("abc")
    result = col._filtered(lambda v: v.startswith("z"))
    assert result.count == 0


def test_basecollection_invalid_value_type():
    with pytest.raises(Exception):
        BaseCollection[str](value="not-a-list")


def test_basecollection_model_validate():
    col = BaseCollection[str].model_validate({"value": ["a", "b", "c"]})
    assert col.count == 3


# ---------------------------------------------------------------------------
# StrIntEnum
# ---------------------------------------------------------------------------


class _Color(StrIntEnum):
    red = 1
    green = 2
    blue = 3


@pytest.mark.parametrize(
    "value, expected",
    [
        ("red", _Color.red),
        ("green", _Color.green),
        ("blue", _Color.blue),
        (1, _Color.red),
        (2, _Color.green),
        (3, _Color.blue),
    ],
)
def test_str_int_enum_validate_valid(value, expected):
    assert _Color.validate(value) == expected


@pytest.mark.parametrize("value", ["purple", "RED", 99, 0])
def test_str_int_enum_validate_invalid(value):
    with pytest.raises(ValueError):
        _Color.validate(value)


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value, expected",
    [
        ("/some/path/file.txt", PurePosixPath("/some/path/file.txt")),
        (PurePosixPath("/already/a/path"), PurePosixPath("/already/a/path")),
        ("relative/path", PurePosixPath("relative/path")),
    ],
)
def test_posix_path_valid(value, expected):
    assert posix_path(value) == expected


def test_posix_path_invalid():
    with pytest.raises(ValueError):
        posix_path(123)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value, expected",
    [
        ("C:\\Windows\\path", PureWindowsPath("C:\\Windows\\path")),
        (PureWindowsPath("C:\\already"), PureWindowsPath("C:\\already")),
        ("\\relative\\win", PureWindowsPath("\\relative\\win")),
    ],
)
def test_windows_path_valid(value, expected):
    assert windows_path(value) == expected


def test_windows_path_invalid():
    with pytest.raises(ValueError):
        windows_path(42)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value, expected",
    [
        ("refs/heads/main", "main"),
        ("main", "main"),
        ("refs/heads/feature/my-feature", "feature/my-feature"),
        ("refs/heads/release/1.0", "release/1.0"),
    ],
)
def test_git_branch_name(value, expected):
    assert git_branch_name(value) == expected


# ---------------------------------------------------------------------------
# Miscellaneous: logs and version
# ---------------------------------------------------------------------------


def test_get_root_logger_returns_logger():
    logger = get_root_logger()
    assert isinstance(logger, logging.Logger)  # noqa: UP038
    assert logger.name == "ez_ados"


def test_version_is_string():
    assert isinstance(__version__, str)
    assert len(__version__) > 0
