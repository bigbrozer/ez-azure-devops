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

__all__ = [
    "BuildDefinition",
    "BuildDefinitionCollection",
    "BuildDefinitionCreate",
    "BuildDefinitionBase",
    "BuildProcess",
    "BuildRepository",
    "Project",
    "Properties",
    "GitItem",
    "GitItemCollection",
    "GitItemDescriptor",
    "GitItemsBatch",
    "GitRef",
    "GitRepository",
    "CommentTypeEnum",
    "ThreadStatusEnum",
    "PullRequestThread",
    "PullRequestThreadCreate",
    "PullRequestThreadCollection",
    "PullRequestThreadComment",
    "PullRequestThreadCommentCreate",
    "GitRefCollection",
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
]
