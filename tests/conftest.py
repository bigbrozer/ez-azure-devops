"""Shared pytest fixtures for the ez_ados test suite."""

from unittest.mock import MagicMock

import niquests
import pytest

# ---------------------------------------------------------------------------
# HTTP mock helpers (module-level, importable from conftest)
# ---------------------------------------------------------------------------


def ok_response(payload: dict | list) -> MagicMock:
    """Return a mock niquests.Response that succeeds and returns *payload*."""
    r = MagicMock()
    r.status_code = 200
    r.json.return_value = payload
    r.text = ""
    return r


def delete_ok_response() -> MagicMock:
    """Return a mock niquests.Response for a successful DELETE (204)."""
    r = MagicMock()
    r.status_code = 204
    r.text = ""
    return r


def error_response(status_code: int, url: str = "https://dev.azure.com") -> MagicMock:
    """Return a mock niquests.Response that raises HTTPError on raise_for_status."""
    r = MagicMock()
    r.status_code = status_code
    r.text = f"HTTP {status_code}"
    r.request = MagicMock()
    r.request.url = url
    exc = niquests.HTTPError("error")
    exc.response = r
    r.raise_for_status.side_effect = exc
    return r


# ---------------------------------------------------------------------------
# Session fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_session() -> MagicMock:
    """Return a MagicMock session ready for injection into any Client subclass."""
    session = MagicMock()
    session.base_url = "https://dev.azure.com/myorg"
    return session


# ---------------------------------------------------------------------------
# Spec dicts (module-level constants, also exposed as fixtures)
# ---------------------------------------------------------------------------

PROJECT_SPEC: dict = {"id": "abc-123", "name": "MyProject"}

GIT_REPOSITORY_SPEC: dict = {
    "id": "repo-abc",
    "name": "MyRepo",
    "project": PROJECT_SPEC,
    "defaultBranch": "refs/heads/main",
    "size": 100,
    "remoteUrl": "https://dev.azure.com/myorg/MyProject/_git/MyRepo",
    "webUrl": "https://dev.azure.com/myorg/MyProject/_git/MyRepo",
    "isDisabled": False,
    "isInMaintenance": False,
}

PIPELINE_SPEC: dict = {
    "id": 1,
    "revision": 1,
    "name": "my-pipeline",
    "folder": "\\Pipelines",
    "url": "https://dev.azure.com/myorg/MyProject/_apis/pipelines/1",
}

POLICY_TYPE_SPEC: dict = {
    "id": "0609b952-1397-4640-95ec-e00a01b2c241",
    "url": "https://dev.azure.com/myorg/MyProject/_apis/policy/types/0609b952-1397-4640-95ec-e00a01b2c241",
    "displayName": "Build",
    "description": "Build policy",
}

POLICY_SCOPE_SPEC: dict = {
    "repositoryId": "repo-abc",
    "refName": "refs/heads/main",
    "matchKind": "Exact",
}

POLICY_SETTINGS_SPEC: dict = {
    "displayName": "Build validation",
    "buildDefinitionId": 42,
    "queueOnSourceUpdateOnly": True,
    "manualQueueOnly": False,
    "validDuration": 720,
    "scope": [POLICY_SCOPE_SPEC],
}

POLICY_CONFIGURATION_SPEC: dict = {
    "id": 1,
    "isEnabled": True,
    "isBlocking": True,
    "isEnterpriseManaged": False,
    "isDeleted": False,
    "settings": POLICY_SETTINGS_SPEC,
    "type": POLICY_TYPE_SPEC,
}

IDENTITY_SPEC: dict = {
    "id": "user-id-123",
    "providerDisplayName": "John Doe",
    "isActive": True,
    "descriptor": "bnd;abc",
    "subjectDescriptor": "vssgp.abc",
}

HOOK_SUBSCRIPTION_SPEC: dict = {
    "id": "sub-123",
    "status": "enabled",
    "publisherId": "tfs",
    "eventType": "git.push",
    "resourceVersion": "1.0-preview.1",
    "eventDescription": "Resource was updated",
    "consumerId": "azureStorageQueue",
    "consumerActionId": "enqueue",
    "actionDescription": "Consumer performed action",
    "publisherInputs": {"branch": "main", "projectId": "proj-1234", "repository": "repo-abc"},
    "consumerInputs": {"accountName": "stafoobar001"},
}

DATETIME_STR = "2024-01-15T10:30:00Z"

PR_COMMENT_SPEC: dict = {
    "id": 1,
    "parentCommentId": 0,
    "publishedDate": DATETIME_STR,
    "lastUpdatedDate": DATETIME_STR,
    "lastContentUpdatedDate": DATETIME_STR,
    "content": "hello",
    "commentType": "text",
}

PR_THREAD_SPEC: dict = {
    "id": 10,
    "publishedDate": DATETIME_STR,
    "lastUpdatedDate": DATETIME_STR,
    "isDeleted": False,
    "comments": [PR_COMMENT_SPEC],
    "properties": None,
}


# --- Fixtures (convenient for parametrize or test methods that receive fixtures) ---


@pytest.fixture
def project_spec() -> dict:
    return dict(PROJECT_SPEC)


@pytest.fixture
def git_repository_spec() -> dict:
    return dict(GIT_REPOSITORY_SPEC)


@pytest.fixture
def pipeline_spec() -> dict:
    return dict(PIPELINE_SPEC)


@pytest.fixture
def policy_type_spec() -> dict:
    return dict(POLICY_TYPE_SPEC)


@pytest.fixture
def policy_configuration_spec() -> dict:
    return dict(POLICY_CONFIGURATION_SPEC)


@pytest.fixture
def identity_spec() -> dict:
    return dict(IDENTITY_SPEC)


@pytest.fixture
def hook_subscription_spec() -> dict:
    return dict(HOOK_SUBSCRIPTION_SPEC)
