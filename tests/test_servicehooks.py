"""Test Service Hooks Models."""

import pydantic
import pytest

from ez_ados.models import HookSubscription, HookSubscriptionCollection, HookSubscriptionCreate


def test_hook_subscription_collection():
    """Test a collection of Service Hooks' Subscription resource."""
    spec = {
        "id": "123",
        "status": "enabled",
        "publisher_id": "tfs",
        "event_type": "git.push",
        "resource_version": "1.0-preview.1",
        "event_description": "Resource was updated",
        "consumer_id": "azureStorageQueue",
        "consumer_action_id": "enqueue",
        "action_description": "Consumer performed action",
        "publisher_inputs": {"branch": "test", "projectId": "1234"},
        "consumer_inputs": {"accountName": "stafoobar001"},
    }
    resources = [
        HookSubscription.model_validate(spec),
        HookSubscription.model_validate(spec | {"event_type": "git.repo.deleted", "status": "disabledBySystem"}),
    ]
    assert resources[0].status.value == 0  # noqa: PLR2004
    assert resources[1].status.value == 30  # noqa: PLR2004

    try:
        results = HookSubscriptionCollection.model_validate({"count": len(resources), "value": resources})
    except pydantic.ValidationError as exc:
        pytest.fail(reason=str(exc))

    with pytest.raises(pydantic.ValidationError):
        HookSubscription(id=1)

    filtered = results.for_git_push_event()
    assert filtered.count == 1  # noqa: PLR2004


def test_hook_subscription_create():
    """Test creation of a Service Hooks' Subscription resource."""
    spec = {
        "publisher_id": "tfs",
        "event_type": "git.push",
        "resource_version": "1.0-preview.1",
        "consumer_id": "azureStorageQueue",
        "consumer_action_id": "enqueue",
        "publisher_inputs": {"branch": "test", "projectId": "1234"},
        "consumer_inputs": {"accountName": "stafoobar001"},
    }
    resource = HookSubscriptionCreate.model_validate(spec)
    assert resource.publisher_id == "tfs"  # noqa: PLR2004
    assert resource.event_type == "git.push"  # noqa: PLR2004
