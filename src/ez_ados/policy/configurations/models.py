"""Models for policy configurations schemas in Azure DevOps."""

from typing import Annotated, Self

from pydantic import Field

from ...base.models import BaseCollection, JSONModel
from ...constants import BUILD_POLICY_TYPE_ID
from ..types.models import PolicyType


class PolicyScope(JSONModel):
    """Represent the scope of a policy."""

    repository_id: Annotated[str | None, Field(alias="repositoryId", default=None)] = None
    ref_name: Annotated[str, Field(alias="refName")]
    match_kind: Annotated[str, Field(alias="matchKind")]


class PolicySettings(JSONModel):
    """Represent settings for a policy configuration."""

    display_name: Annotated[str | None, Field(alias="displayName")]
    build_definition_id: Annotated[int, Field(alias="buildDefinitionId")]
    never_expire: Annotated[bool, Field(alias="queueOnSourceUpdateOnly", default=False)] = False
    manual_trigger: Annotated[bool, Field(alias="manualQueueOnly", default=False)] = False
    valid_duration: Annotated[int, Field(alias="validDuration", default=0)] = 0
    scope: list[PolicyScope]


class PolicyConfigurationPayload(JSONModel):
    """Fields shared by create and update requests for a policy configuration."""

    enabled: Annotated[bool, Field(alias="isEnabled")]
    required: Annotated[bool, Field(alias="isBlocking")]
    enterprise_managed: Annotated[bool, Field(alias="isEnterpriseManaged", default=False)] = False
    settings: PolicySettings
    type: PolicyType


class PolicyConfiguration(PolicyConfigurationPayload):
    """Represent a policy configuration returned by the API."""

    id: int
    deleted: Annotated[bool, Field(alias="isDeleted")]


class PolicyConfigurationCollection(BaseCollection[PolicyConfiguration]):
    """Represent a collection of policy configuration."""

    def _is_build_type(self, policy: PolicyConfiguration) -> bool:
        return not policy.deleted and policy.type.id == BUILD_POLICY_TYPE_ID

    def get_build_policies(self) -> Self:
        """Return list of build policies from a collection of policy configuration."""
        return self._filtered(self._is_build_type)

    def match_build_definition(self, id: int) -> Self:
        """Return list of build policies that match build definition by ID."""
        return self._filtered(lambda p: self._is_build_type(p) and p.settings.build_definition_id == id)
