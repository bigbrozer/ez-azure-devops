"""Module for loading Azure DevOps API models."""

from .builds.models import (
    BuildDefinition,
    BuildDefinitionBase,
    BuildDefinitionCollection,
    BuildDefinitionCreate,
    BuildProcess,
    BuildRepository,
)
from .core.models import Project, Properties
from .git.models import (
    GitItem,
    GitItemCollection,
    GitItemDescriptor,
    GitItemsBatch,
    GitRef,
    GitRefCollection,
    GitRepository,
)
from .git.pullrequests.enums import CommentTypeEnum, ThreadStatusEnum
from .git.pullrequests.models import (
    PullRequestThread,
    PullRequestThreadCollection,
    PullRequestThreadComment,
    PullRequestThreadCommentCreate,
    PullRequestThreadCreate,
)
from .pipelines.models import (
    Pipeline,
    PipelineCollection,
    PipelineConfiguration,
    PipelineConfigurationRepository,
    PipelineCreate,
)
from .policy.configurations.models import (
    PolicyConfiguration,
    PolicyConfigurationCollection,
    PolicyConfigurationCreate,
    PolicyConfigurationUpdate,
    PolicyScope,
    PolicySettings,
    PolicyType,
)
from .servicehooks.subscriptions.models import HookSubscription, HookSubscriptionCollection, HookSubscriptionCreate

__all__ = [
    "BuildDefinition",
    "BuildDefinitionBase",
    "BuildDefinitionCollection",
    "BuildDefinitionCreate",
    "BuildProcess",
    "BuildRepository",
    "CommentTypeEnum",
    "GitItem",
    "GitItemCollection",
    "GitItemDescriptor",
    "GitItemsBatch",
    "GitRef",
    "GitRefCollection",
    "GitRepository",
    "HookSubscription",
    "HookSubscriptionCollection",
    "HookSubscriptionCreate",
    "Pipeline",
    "PipelineCollection",
    "PipelineConfiguration",
    "PipelineConfigurationRepository",
    "PipelineCreate",
    "PolicyConfiguration",
    "PolicyConfigurationCollection",
    "PolicyConfigurationCreate",
    "PolicyConfigurationUpdate",
    "PolicyScope",
    "PolicySettings",
    "PolicyType",
    "Project",
    "Properties",
    "PullRequestThread",
    "PullRequestThreadCollection",
    "PullRequestThreadComment",
    "PullRequestThreadCommentCreate",
    "PullRequestThreadCreate",
    "ThreadStatusEnum",
]
