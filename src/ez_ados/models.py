"""Module for loading Azure DevOps API models."""

from .builds.models import (
    BuildDefinition,
    BuildDefinitionCollection,
    BuildDefinitionCreate,
    BuildDefinitionSummary,
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
from .git.pullrequests.enums import CommentTypeEnum, ThreadStatusEnum, VoteEnum
from .git.pullrequests.models import (
    IdentityRefCreate,
    IdentityRefWithVote,
    IdentityRefWithVoteCollection,
    PullRequestThread,
    PullRequestThreadCollection,
    PullRequestThreadComment,
    PullRequestThreadCommentCreate,
    PullRequestThreadCreate,
)
from .identities.models import Identity, IdentityCollection
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
    PolicyConfigurationPayload,
    PolicyScope,
    PolicySettings,
)
from .policy.types.models import PolicyType
from .servicehooks.subscriptions.models import HookSubscription, HookSubscriptionCollection, HookSubscriptionCreate

__all__ = [
    "BuildDefinition",
    "BuildDefinitionCollection",
    "BuildDefinitionCreate",
    "BuildDefinitionSummary",
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
    "IdentityRefCreate",
    "IdentityRefWithVote",
    "IdentityRefWithVoteCollection",
    "HookSubscription",
    "HookSubscriptionCollection",
    "HookSubscriptionCreate",
    "Identity",
    "IdentityCollection",
    "Pipeline",
    "PipelineCollection",
    "PipelineConfiguration",
    "PipelineConfigurationRepository",
    "PipelineCreate",
    "PolicyConfiguration",
    "PolicyConfigurationCollection",
    "PolicyConfigurationPayload",
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
    "VoteEnum",
]
