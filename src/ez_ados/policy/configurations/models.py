"""Models for policy configurations schemas in Azure DevOps."""

from typing import Annotated, Self

from pydantic import Field

from ...base.models import BaseCollection, JSONModel
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


class PolicyConfigurationBase(JSONModel):
    """Represent a request to create a policy configuration."""

    enabled: Annotated[bool, Field(alias="isEnabled")]
    required: Annotated[bool, Field(alias="isBlocking")]
    enterprise_managed: Annotated[bool, Field(alias="isEnterpriseManaged", default=False)] = False
    settings: PolicySettings
    type: PolicyType


class PolicyConfigurationCreate(PolicyConfigurationBase):
    """Represent a request to create a policy configuration."""


class PolicyConfigurationUpdate(PolicyConfigurationBase):
    """Represent a request to update a policy configuration."""


class PolicyConfiguration(PolicyConfigurationBase):
    """Represent a policy configuration."""

    id: int
    deleted: Annotated[bool, Field(alias="isDeleted")]


class PolicyConfigurationCollection(BaseCollection[PolicyConfiguration]):
    """Represent a collection of policy configuration."""

    def _is_build_type(self, policy: PolicyConfiguration) -> bool:
        return not policy.deleted and policy.type.id == "0609b952-1397-4640-95ec-e00a01b2c241"

    def get_build_policies(self) -> Self:
        """Return list of build policies from a collection of policy configuration."""

        def _filter(policy: PolicyConfiguration) -> bool:
            return self._is_build_type(policy)

        filtered_results = list(filter(_filter, self))
        return type(self)(count=len(filtered_results), value=filtered_results)

    def match_build_definition(self, id: int) -> Self:
        """Return list of build policies that match build definition by ID."""

        def _filter(policy: PolicyConfiguration) -> bool:
            if self._is_build_type(policy):
                return policy.settings.build_definition_id == id
            else:
                return False

        filtered_results = list(filter(_filter, self))
        return type(self)(count=len(filtered_results), value=filtered_results)
