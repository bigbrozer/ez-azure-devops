"""Tests for service hook models and HookSubscriptionClient."""

from unittest.mock import MagicMock

import pydantic
import pytest

from conftest import HOOK_SUBSCRIPTION_SPEC, ok_response

from ez_ados.servicehooks.subscriptions.clients import HookSubscriptionClient
from ez_ados.servicehooks.subscriptions.enums import SubscriptionStatus
from ez_ados.servicehooks.subscriptions.models import (
    HookSubscription,
    HookSubscriptionCollection,
    HookSubscriptionCreate,
)

# ---------------------------------------------------------------------------
# SubscriptionStatus enum
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value, expected",
    [
        ("enabled", SubscriptionStatus.enabled),
        ("onProbation", SubscriptionStatus.onProbation),
        ("disabledByUser", SubscriptionStatus.disabledByUser),
        ("disabledBySystem", SubscriptionStatus.disabledBySystem),
        ("disabledByInactiveIdentity", SubscriptionStatus.disabledByInactiveIdentity),
        (0, SubscriptionStatus.enabled),
        (10, SubscriptionStatus.onProbation),
        (20, SubscriptionStatus.disabledByUser),
        (30, SubscriptionStatus.disabledBySystem),
        (40, SubscriptionStatus.disabledByInactiveIdentity),
    ],
)
def test_subscription_status_validate(value, expected):
    assert SubscriptionStatus.validate(value) == expected


@pytest.mark.parametrize("bad", ["active", 99])
def test_subscription_status_invalid(bad):
    with pytest.raises(ValueError):
        SubscriptionStatus.validate(bad)


# ---------------------------------------------------------------------------
# HookSubscription model
# ---------------------------------------------------------------------------


def test_hook_subscription_valid(hook_subscription_spec):
    sub = HookSubscription.model_validate(hook_subscription_spec)
    assert sub.id == "sub-123"
    assert sub.status == SubscriptionStatus.enabled
    assert sub.event_type == "git.push"
    assert sub.publisher_inputs["branch"] == "main"


def test_hook_subscription_camelcase_wire_format():
    """The API sends camelCase keys; the model must accept them."""
    sub = HookSubscription.model_validate(HOOK_SUBSCRIPTION_SPEC)
    assert sub.publisher_id == "tfs"
    assert sub.consumer_id == "azureStorageQueue"


def test_hook_subscription_invalid_id_type():
    with pytest.raises(pydantic.ValidationError):
        HookSubscription.model_validate({**HOOK_SUBSCRIPTION_SPEC, "id": None})


# ---------------------------------------------------------------------------
# HookSubscriptionCollection.for_event
# ---------------------------------------------------------------------------


def _make_collection(*specs: dict) -> HookSubscriptionCollection:
    col = HookSubscriptionCollection()
    for spec in specs:
        col.append(HookSubscription.model_validate(spec))
    return col


def test_for_event_matches():
    col = _make_collection(
        HOOK_SUBSCRIPTION_SPEC,
        {**HOOK_SUBSCRIPTION_SPEC, "id": "sub-2", "eventType": "git.repo.deleted"},
    )
    result = col.for_event("git.push")
    assert result.count == 1
    assert result[0].event_type == "git.push"


def test_for_event_no_match():
    col = _make_collection(HOOK_SUBSCRIPTION_SPEC)
    assert col.for_event("git.pullrequest.created").count == 0


# ---------------------------------------------------------------------------
# HookSubscriptionCollection.for_git_push_event
# ---------------------------------------------------------------------------

_PUSH_BASE = HOOK_SUBSCRIPTION_SPEC  # branch=main, projectId=proj-1234, repository=repo-abc
_PUSH_OTHER_BRANCH = {
    **HOOK_SUBSCRIPTION_SPEC,
    "id": "sub-2",
    "publisherInputs": {"branch": "dev", "projectId": "proj-1234", "repository": "repo-abc"},
}
_PUSH_OTHER_PROJECT = {
    **HOOK_SUBSCRIPTION_SPEC,
    "id": "sub-3",
    "publisherInputs": {"branch": "main", "projectId": "other-proj", "repository": "repo-abc"},
}
_PUSH_OTHER_REPO = {
    **HOOK_SUBSCRIPTION_SPEC,
    "id": "sub-4",
    "publisherInputs": {"branch": "main", "projectId": "proj-1234", "repository": "other-repo"},
}
_NON_PUSH = {**HOOK_SUBSCRIPTION_SPEC, "id": "sub-5", "eventType": "git.repo.deleted", "status": "disabledBySystem"}


@pytest.mark.parametrize(
    "kwargs, expected_ids",
    [
        ({}, ["sub-123", "sub-2", "sub-3", "sub-4"]),
        ({"branch_name": "main"}, ["sub-123", "sub-3", "sub-4"]),
        ({"branch_name": "dev"}, ["sub-2"]),
        ({"project_id": "proj-1234"}, ["sub-123", "sub-2", "sub-4"]),
        ({"repository_id": "repo-abc"}, ["sub-123", "sub-2", "sub-3"]),
        ({"branch_name": "main", "project_id": "proj-1234"}, ["sub-123", "sub-4"]),
        ({"branch_name": "main", "project_id": "proj-1234", "repository_id": "repo-abc"}, ["sub-123"]),
    ],
)
def test_for_git_push_event_filters(kwargs, expected_ids):
    col = _make_collection(_PUSH_BASE, _PUSH_OTHER_BRANCH, _PUSH_OTHER_PROJECT, _PUSH_OTHER_REPO, _NON_PUSH)
    result = col.for_git_push_event(**kwargs)
    assert sorted(s.id for s in result) == sorted(expected_ids)


# ---------------------------------------------------------------------------
# HookSubscriptionCreate
# ---------------------------------------------------------------------------


def test_hook_subscription_create_valid():
    spec = {
        "publisherId": "tfs",
        "eventType": "git.push",
        "resourceVersion": "1.0-preview.1",
        "consumerId": "azureStorageQueue",
        "consumerActionId": "enqueue",
        "publisherInputs": {"branch": "main", "projectId": "proj-1234"},
        "consumerInputs": {"accountName": "myaccount"},
    }
    sub = HookSubscriptionCreate.model_validate(spec)
    assert sub.publisher_id == "tfs"
    assert sub.event_type == "git.push"


def test_hook_subscription_create_snake_case_input():
    spec = {
        "publisher_id": "tfs",
        "event_type": "git.push",
        "resource_version": "1.0-preview.1",
        "consumer_id": "azureStorageQueue",
        "consumer_action_id": "enqueue",
        "publisher_inputs": {"branch": "main"},
        "consumer_inputs": {"accountName": "myaccount"},
    }
    sub = HookSubscriptionCreate.model_validate(spec)
    assert sub.publisher_id == "tfs"


# ---------------------------------------------------------------------------
# HookSubscriptionClient
# ---------------------------------------------------------------------------


def test_hook_client_get(mock_session, hook_subscription_spec):
    mock_session.get.return_value = ok_response(hook_subscription_spec)
    client = HookSubscriptionClient(mock_session)

    result = client.get("sub-123")

    assert isinstance(result, HookSubscription)
    assert result.id == "sub-123"
    mock_session.get.assert_called_once_with("sub-123", params=None)


def test_hook_client_list(mock_session, hook_subscription_spec):
    payload = {"value": [hook_subscription_spec]}
    mock_session.get.return_value = ok_response(payload)
    client = HookSubscriptionClient(mock_session)

    result = client.list()

    assert isinstance(result, HookSubscriptionCollection)
    assert result.count == 1
    mock_session.get.assert_called_once_with("", params=None)


def test_hook_client_delete(mock_session):
    del_resp = MagicMock()
    del_resp.status_code = 204
    mock_session.delete.return_value = del_resp
    client = HookSubscriptionClient(mock_session)

    client.delete("sub-123")

    mock_session.delete.assert_called_once_with("sub-123", params=None)


def test_hook_client_create(mock_session, hook_subscription_spec):
    mock_session.post.return_value = ok_response(hook_subscription_spec)
    client = HookSubscriptionClient(mock_session)

    definition = HookSubscriptionCreate.model_validate(
        {
            "publisherId": "tfs",
            "eventType": "git.push",
            "resourceVersion": "1.0-preview.1",
            "consumerId": "azureStorageQueue",
            "consumerActionId": "enqueue",
            "publisherInputs": {"branch": "main", "projectId": "proj-1234"},
            "consumerInputs": {"accountName": "myaccount"},
        }
    )
    result = client.create(definition)

    assert isinstance(result, HookSubscription)
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert call_args[0][0] == ""
