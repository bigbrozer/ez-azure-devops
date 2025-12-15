"""Module for Service Hooks' Subscriptions models."""

from typing import Annotated, Any, Self

from pydantic import BeforeValidator, Field

from ...base.models import BaseCollection, JSONModel
from .enums import SubscriptionStatus


class HookSubscription(JSONModel):
    """Represents a hook subscription."""

    id: str
    status: Annotated[SubscriptionStatus, BeforeValidator(SubscriptionStatus.validate)]
    publisher_id: Annotated[str, Field(alias="publisherId")]
    event_type: Annotated[str, Field(alias="eventType")]
    resource_version: Annotated[str, Field(alias="resourceVersion")]
    event_description: Annotated[str, Field(alias="eventDescription")]
    consumer_id: Annotated[str, Field(alias="consumerId")]
    consumer_action_id: Annotated[str, Field(alias="consumerActionId")]
    action_description: Annotated[str, Field(alias="actionDescription")]
    publisher_inputs: Annotated[dict[str, Any], Field(alias="publisherInputs")]
    consumer_inputs: Annotated[dict[str, Any], Field(alias="consumerInputs")]


class HookSubscriptionCreate(JSONModel):
    """Creates a new hook subscription."""

    publisher_id: Annotated[str, Field(alias="publisherId")]
    event_type: Annotated[str, Field(alias="eventType")]
    resource_version: Annotated[str, Field(alias="resourceVersion")]
    consumer_id: Annotated[str, Field(alias="consumerId")]
    consumer_action_id: Annotated[str, Field(alias="consumerActionId")]
    publisher_inputs: Annotated[dict[str, Any], Field(alias="publisherInputs")]
    consumer_inputs: Annotated[dict[str, Any], Field(alias="consumerInputs")]


class HookSubscriptionCollection(BaseCollection[HookSubscription]):
    """Represents a collection of hook subscriptions."""

    def for_event(self, event_type: str) -> Self:
        """Filter hook subscription for a type of event."""

        def _filter(p: HookSubscription) -> bool:
            return p.event_type == event_type

        filtered_results = list(filter(_filter, self))
        return type(self)(count=len(filtered_results), value=filtered_results)

    def for_git_push_event(
        self, branch_name: str | None = None, project_id: str | None = None, repository_id: str | None = None
    ) -> Self:
        """Filter hook subscription for a git.push event."""
        _filtered_events = self.for_event("git.push")

        def _filter(p: HookSubscription) -> bool:
            if p.event_type == "git.push":
                if branch_name is not None and p.publisher_inputs["branch"] != branch_name:
                    return False
                if project_id is not None and p.publisher_inputs["projectId"] != project_id:
                    return False
                if repository_id is not None and p.publisher_inputs["repository"] != repository_id:
                    return False
                return True
            else:
                return False

        filtered_results = list(filter(_filter, _filtered_events))
        return type(self)(count=len(filtered_results), value=filtered_results)
