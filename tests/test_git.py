"""Tests for git models and GitRepositoryClient."""

from pathlib import PurePosixPath
from unittest.mock import MagicMock

import pydantic
import pytest

from conftest import GIT_REPOSITORY_SPEC, ok_response

from ez_ados.git.clients import GitRepositoryClient
from ez_ados.git.enums import GitObjectType, RecursionType
from ez_ados.git.models import (
    GitItem,
    GitItemCollection,
    GitItemDescriptor,
    GitItemsBatch,
    GitRef,
    GitRefCollection,
    GitRepository,
)

# ---------------------------------------------------------------------------
# GitRepository
# ---------------------------------------------------------------------------


def test_git_repository_valid(git_repository_spec):
    repo = GitRepository.model_validate(git_repository_spec)
    assert repo.id == "repo-abc"
    assert repo.name == "MyRepo"
    assert repo.default_branch == "refs/heads/main"
    assert repo.disabled is False


def test_git_repository_invalid_id_type():
    with pytest.raises(pydantic.ValidationError):
        GitRepository.model_validate({**GIT_REPOSITORY_SPEC, "id": 123})


# ---------------------------------------------------------------------------
# GitRef
# ---------------------------------------------------------------------------


def test_git_ref_valid():
    ref = GitRef.model_validate({"name": "refs/heads/main", "objectId": "abc123"})
    assert ref.name == "refs/heads/main"
    assert ref.object_id == "abc123"
    assert ref.locked is None


def test_git_ref_with_locked():
    ref = GitRef.model_validate({"name": "refs/heads/locked", "objectId": "def456", "isLocked": True})
    assert ref.locked is True


def test_git_ref_invalid_locked_type():
    # Pydantic v2 coerces many strings to bool; use a dict which is not coercible
    with pytest.raises(pydantic.ValidationError):
        GitRef.model_validate({"name": "refs/heads/main", "objectId": "abc", "isLocked": {"invalid": True}})


def test_git_ref_collection():
    data = {
        "value": [
            {"name": "refs/heads/main", "objectId": "a"},
            {"name": "refs/heads/dev", "objectId": "b", "isLocked": False},
        ]
    }
    col = GitRefCollection.model_validate(data)
    assert col.count == 2
    assert col[0].name == "refs/heads/main"


# ---------------------------------------------------------------------------
# GitItemDescriptor and GitItemsBatch
# ---------------------------------------------------------------------------


def test_git_item_descriptor_defaults():
    desc = GitItemDescriptor(path="/src", version="main")
    assert desc.path == PurePosixPath("/src")
    assert desc.recursion_level == RecursionType.full
    assert desc.version_type == "branch"


def test_git_item_descriptor_recursion_coercion():
    desc = GitItemDescriptor(path="/", version="main", recursionLevel="oneLevel")
    assert desc.recursion_level == RecursionType.oneLevel


def test_git_items_batch_construction():
    batch = GitItemsBatch(
        itemDescriptors=[{"path": "/src", "version": "main"}],
    )
    assert len(batch.item_descriptors) == 1
    assert batch.include_links is False


# ---------------------------------------------------------------------------
# GitItem
# ---------------------------------------------------------------------------


_ITEM_BLOB = {"objectId": "abc", "gitObjectType": "blob", "path": "/src/main.py"}
_ITEM_TREE = {"objectId": "def", "gitObjectType": "tree", "path": "/src", "isFolder": True}


@pytest.mark.parametrize(
    "raw_type, expected",
    [
        ("blob", GitObjectType.blob),
        ("tree", GitObjectType.tree),
        ("commit", GitObjectType.commit),
        (3, GitObjectType.blob),
    ],
)
def test_git_item_object_type_coercion(raw_type, expected):
    item = GitItem.model_validate({"objectId": "x", "gitObjectType": raw_type, "path": "/f"})
    assert item.git_object_type == expected


def test_git_item_path_as_posix_path():
    item = GitItem.model_validate(_ITEM_BLOB)
    assert item.path == PurePosixPath("/src/main.py")


# ---------------------------------------------------------------------------
# GitItemCollection.match
# ---------------------------------------------------------------------------

_ITEMS_DATA = {
    "value": [
        {"objectId": "a", "gitObjectType": "blob", "path": "/src/models.py"},
        {"objectId": "b", "gitObjectType": "blob", "path": "/src/clients.py"},
        {"objectId": "c", "gitObjectType": "blob", "path": "/tests/test_models.py"},
        {"objectId": "d", "gitObjectType": "tree", "path": "/src"},
    ]
}


@pytest.mark.parametrize(
    "pattern, expected_count",
    [
        ("*.py", 3),
        ("src/*.py", 2),
        ("tests/*.py", 1),
        ("*.txt", 0),
    ],
)
def test_git_item_collection_match(pattern, expected_count):
    col = GitItemCollection.model_validate(_ITEMS_DATA)
    result = col.match(pattern)
    assert result.count == expected_count


# ---------------------------------------------------------------------------
# GitRepositoryClient
# ---------------------------------------------------------------------------


def test_git_client_get(mock_session, git_repository_spec):
    mock_session.get.return_value = ok_response(git_repository_spec)
    client = GitRepositoryClient(mock_session)

    result = client.get("MyRepo")

    assert isinstance(result, GitRepository)
    assert result.id == "repo-abc"
    mock_session.get.assert_called_once_with("MyRepo", params=None)


def test_git_client_get_refs_no_filter(mock_session):
    payload = {"value": [{"name": "refs/heads/main", "objectId": "abc"}, {"name": "refs/heads/dev", "objectId": "def"}]}
    mock_session.get.return_value = ok_response(payload)
    client = GitRepositoryClient(mock_session)

    result = client.get_refs("MyRepo")

    assert isinstance(result, GitRefCollection)
    assert result.count == 2
    mock_session.get.assert_called_once_with("/MyRepo/refs", params=None)


def test_git_client_get_refs_with_branch_filter(mock_session):
    payload = {"value": [{"name": "refs/heads/main", "objectId": "abc"}]}
    mock_session.get.return_value = ok_response(payload)
    client = GitRepositoryClient(mock_session)

    client.get_refs("MyRepo", branch_startswith="refs/heads/main")

    call_args = mock_session.get.call_args
    params = call_args[1].get("params") or {}
    assert "filter" in params
    assert params["filter"] == "heads/main"


def test_git_client_get_items_batch(mock_session):
    payload = {
        "value": [
            [
                {"objectId": "a", "gitObjectType": "blob", "path": "/src/main.py"},
                {"objectId": "b", "gitObjectType": "blob", "path": "/src/utils.py"},
            ]
        ]
    }
    response = ok_response(payload)
    response.url = "https://example.com/itemsbatch"
    mock_session.post.return_value = response
    client = GitRepositoryClient(mock_session)

    batch = GitItemsBatch(itemDescriptors=[{"path": "/src", "version": "main"}])
    result = client.get_items_batch("MyRepo", batch)

    assert isinstance(result, GitItemCollection)
    assert result.count == 2
    mock_session.post.assert_called_once()


def test_git_client_get_item_with_str_path(mock_session):
    item_payload = {"objectId": "abc", "gitObjectType": "blob", "path": "/src/main.py", "content": "print('hi')"}
    response = ok_response(item_payload)
    response.url = "https://example.com"
    mock_session.get.return_value = response
    client = GitRepositoryClient(mock_session)

    result = client.get_item("MyRepo", "/src/main.py")

    assert isinstance(result, GitItem)
    assert result.content == "print('hi')"


def test_git_client_get_item_with_posix_path(mock_session):
    item_payload = {"objectId": "abc", "gitObjectType": "blob", "path": "/src/main.py"}
    response = ok_response(item_payload)
    response.url = "https://example.com"
    mock_session.get.return_value = response
    client = GitRepositoryClient(mock_session)

    result = client.get_item("MyRepo", PurePosixPath("/src/main.py"))

    assert isinstance(result, GitItem)


def test_git_client_get_item_with_branch(mock_session):
    item_payload = {"objectId": "abc", "gitObjectType": "blob", "path": "/src/main.py"}
    response = ok_response(item_payload)
    response.url = "https://example.com"
    mock_session.get.return_value = response
    client = GitRepositoryClient(mock_session)

    client.get_item("MyRepo", "/src/main.py", branch="feature/xyz")

    call_kwargs = mock_session.get.call_args[1]
    assert call_kwargs["params"]["versionDescriptor.version"] == "feature/xyz"


def test_git_client_get_item_invalid_path_type(mock_session):
    client = GitRepositoryClient(mock_session)
    with pytest.raises(ValueError, match="path argument"):
        client.get_item("MyRepo", 123)  # type: ignore[arg-type]


def test_git_client_list_files(mock_session):
    batch_payload = {"value": [[{"objectId": "a", "gitObjectType": "blob", "path": "/src/main.py"}]]}
    response = ok_response(batch_payload)
    response.url = "https://example.com"
    mock_session.post.return_value = response
    client = GitRepositoryClient(mock_session)

    result = client.list_files("MyRepo", "main", "/src")

    assert isinstance(result, GitItemCollection)
    mock_session.post.assert_called_once()


def test_git_client_is_branch_locked_true(mock_session):
    payload = {"value": [{"name": "refs/heads/main", "objectId": "abc", "isLocked": True}]}
    mock_session.get.return_value = ok_response(payload)
    client = GitRepositoryClient(mock_session)

    assert client.is_branch_locked("MyRepo", "refs/heads/main") is True


def test_git_client_is_branch_locked_false(mock_session):
    payload = {"value": [{"name": "refs/heads/main", "objectId": "abc", "isLocked": False}]}
    mock_session.get.return_value = ok_response(payload)
    client = GitRepositoryClient(mock_session)

    assert client.is_branch_locked("MyRepo", "refs/heads/main") is False


def test_git_client_is_branch_locked_none(mock_session):
    payload = {"value": [{"name": "refs/heads/main", "objectId": "abc"}]}
    mock_session.get.return_value = ok_response(payload)
    client = GitRepositoryClient(mock_session)

    assert client.is_branch_locked("MyRepo", "refs/heads/main") is False


def test_git_client_lock_branch_toggle(mock_session):
    lock_response = MagicMock()
    lock_response.status_code = 200
    lock_response.json.return_value = [{"name": "refs/heads/main", "isLocked": True}]
    mock_session.patch.return_value = lock_response
    client = GitRepositoryClient(mock_session)

    result = client.lock_branch_toggle("MyRepo", "refs/heads/main", locked=True)

    assert isinstance(result, list)
    mock_session.patch.assert_called_once()
