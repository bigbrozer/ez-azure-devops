"""Test Azure DevOps Models."""

import pydantic
import pytest

from ez_ados.models import (
    BuildDefinitionCreate,
    BuildProcess,
    BuildRepository,
    GitItem,
    GitItemCollection,
    GitItemDescriptor,
    GitItemsBatch,
    GitRef,
    GitRefCollection,
    GitRepository,
    Pipeline,
    PipelineCollection,
    PolicyConfiguration,
    PolicyConfigurationCollection,
    Project,
    PullRequestThread,
    PullRequestThreadCollection,
    PullRequestThreadCommentCreate,
    PullRequestThreadCreate,
)


def test_build_definition_create():
    """Test Build Definition resource instantiation."""
    resource = BuildDefinitionCreate(
        name="test",
        path="/ci",
        process=BuildProcess(yaml_filename="/my/folder/ci.yaml"),
        repository=BuildRepository(id="1234"),
    )
    assert resource.name == "test"

    with pytest.raises(pydantic.ValidationError):
        BuildDefinitionCreate(
            name="test",
            path="/ci",
            process="whatever",
            repository="1234",
        )


def test_git_item():
    """Test Git Item resource instantiation."""
    resources = [
        GitItem(objectId="1452645214266465", gitObjectType="blob", path="tests/folder"),
        GitItem(objectId="9809798755", gitObjectType="commit", path="tests/folder"),
    ]
    assert resources[0].git_object_type.value == 3  # noqa: PLR2004
    assert resources[1].git_object_type.value == 1

    try:
        collection = GitItemCollection.model_validate({"count": len(resources), "value": resources})
        assert collection.count == 2  # noqa: PLR2004
    except pydantic.ValidationError as exc:
        pytest.fail(reason=str(exc))

    with pytest.raises(pydantic.ValidationError):
        GitItem(objectId="1452645214266465", gitObjectType="foo")


def test_git_item_batch_body():
    """Test Git Item Batch Body resource instantiation."""
    resources = [
        GitItemDescriptor(path="/a/folder", version="main", recursionLevel="full"),
        GitItemDescriptor(path="/b/folder", version="main", recursionLevel="oneLevel"),
    ]
    assert resources[0].recursion_level.value == 120  # noqa: PLR2004
    assert resources[1].recursion_level.value == 1  # noqa: PLR2004

    try:
        GitItemsBatch.model_validate({"itemDescriptors": resources})
    except pydantic.ValidationError as exc:
        pytest.fail(reason=str(exc))

    with pytest.raises(pydantic.ValidationError):
        GitItemDescriptor(path="/a/folder", version="main", recursionLevel="foo")


def test_git_ref():
    """Test Git Ref resource instantiation."""
    resources = [
        GitRef(objectId="123456", name="refs/heads/main"),
        GitRef(objectId="7890", name="refs/heads/develop"),
    ]
    assert resources[0].name == "refs/heads/main"
    assert resources[1].name == "refs/heads/develop"

    try:
        collection = GitRefCollection.model_validate({"count": len(resources), "value": resources})
        assert collection.count == 2  # noqa: PLR2004
    except pydantic.ValidationError as exc:
        pytest.fail(reason=str(exc))

    with pytest.raises(pydantic.ValidationError):
        GitRef(objectId="123456", name="refs/heads/main", isLocked="foo")


def test_project():
    """Test Project resource instantiation."""
    resource = Project(id="1234-456", name="my-project")
    assert resource.name == "my-project"

    with pytest.raises(pydantic.ValidationError):
        Project(id=1, name="my-project")


def test_git_repository():
    """Test Git Repository resource instantiation."""
    spec = {
        "id": "1234",
        "name": "my-repo",
        "defaultBranch": "refs/heads/main",
        "isDisabled": False,
        "isInMaintenance": False,
        "project": {"id": "1234", "name": "my-project"},
        "remoteUrl": "https://...",
        "webUrl": "https://...",
        "size": 0,
    }
    resource = GitRepository.model_validate(spec)
    assert resource.name == "my-repo"

    with pytest.raises(pydantic.ValidationError):
        GitRepository.model_validate(spec | {"id": 123})


def test_pipeline():
    """Test Pipeline resource instantiation."""
    resource = Pipeline(id=1, name="my-pipeline", folder="/my-folder", url="https://example.com", revision=1)
    assert resource.name == "my-pipeline"

    with pytest.raises(pydantic.ValidationError):
        Pipeline(id="foo", name="bad-pipeline", folder="a:bad:folder", url="https://example.com", revision=1)


def test_pipeline_collection():
    """Test collection of Pipelines instantiation."""
    try:
        pipelines = [
            Pipeline(id=1, name="my-ci", folder="/ci", url="https://example.com", revision=1),
            Pipeline(id=2, name="my-cd", folder="/cd", url="https://example.com", revision=1),
        ]
        collection = PipelineCollection.model_validate({"count": len(pipelines), "value": pipelines})
        assert collection.count == 2  # noqa: PLR2004
    except pydantic.ValidationError as exc:
        pytest.fail(reason=str(exc))

    assert collection.startswith("my-")[0].name == "my-ci"
    assert collection.from_folder("/cd")[0].name == "my-cd"


def test_policy_configuration():
    """Test Policy Configuration resource instantiation."""
    spec = {
        "id": 1,
        "isEnabled": True,
        "isBlocking": True,
        "isDeleted": False,
        "isEnterpriseManaged": False,
        "settings": {
            "displayName": "Build",
            "buildDefinitionId": 10,
            "scope": [{"repositoryId": "1234", "refName": "refs/heads/main", "matchKind": "commit"}],
        },
        "type": {"id": "1123-4556", "url": "https://...", "displayName": "Build", "description": "hey"},
    }
    resources = [
        PolicyConfiguration.model_validate(spec),
        PolicyConfiguration.model_validate(spec | {"id": 2}),
    ]
    assert resources[0].settings.display_name == "Build"

    try:
        collection = PolicyConfigurationCollection.model_validate({"count": len(resources), "value": resources})
        assert collection.count == 2  # noqa: PLR2004
    except pydantic.ValidationError as exc:
        pytest.fail(reason=str(exc))

    with pytest.raises(pydantic.ValidationError):
        PolicyConfiguration.model_validate(spec | {"id": "foo"})


def test_git_pull_request_thread():
    """Test Git Pull Request Thread resource instantiation."""
    spec = {
        "id": 1,
        "publishedDate": "2025-10-03T12:46:41.42Z",
        "lastUpdatedDate": "2025-10-03T12:46:41.42Z",
        "isDeleted": False,
        "comments": [
            {
                "id": 1,
                "parentCommentId": 0,
                "content": "Policy status has been updated",
                "publishedDate": "2025-10-03T12:46:41.42Z",
                "lastUpdatedDate": "2025-10-03T12:46:41.42Z",
                "lastContentUpdatedDate": "2025-10-03T12:46:41.42Z",
                "commentType": "system",
            }
        ],
    }
    resources = [
        PullRequestThread.model_validate(spec),
        PullRequestThread.model_validate(spec | {"isDeleted": True}),
    ]
    assert not resources[0].deleted
    assert resources[1].deleted

    try:
        collection = PullRequestThreadCollection.model_validate({"count": len(resources), "value": resources})
        assert collection.count == 2  # noqa: PLR2004
    except pydantic.ValidationError as exc:
        pytest.fail(reason=str(exc))

    with pytest.raises(pydantic.ValidationError):
        PullRequestThread.model_validate(spec | {"id": "foo"})


def test_git_pull_request_thread_body():
    """Test Git Pull Request Thread Body request instantiation."""
    resource = PullRequestThreadCreate(comments=[PullRequestThreadCommentCreate(content="Test")])
    assert resource.comments[0].content == "Test"

    with pytest.raises(pydantic.ValidationError):
        PullRequestThreadCreate(comments=1)
