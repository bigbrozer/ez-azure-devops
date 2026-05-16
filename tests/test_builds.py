"""Tests for builds models and BuildClient."""

from pathlib import PurePosixPath, PureWindowsPath
from unittest.mock import MagicMock

import pydantic
import pytest

from conftest import PROJECT_SPEC, ok_response

from ez_ados.builds.clients import BuildClient
from ez_ados.builds.models import (
    BuildDefinition,
    BuildDefinitionCollection,
    BuildDefinitionCreate,
    BuildDefinitionSummary,
    BuildProcess,
    BuildRepository,
)
from ez_ados.core.models import Properties
from ez_ados.git.models import GitRepository

# ---------------------------------------------------------------------------
# BuildProcess
# ---------------------------------------------------------------------------


def test_build_process_valid():
    bp = BuildProcess(yamlFilename="/pipelines/build.yml")
    assert bp.yaml_filename == PurePosixPath("/pipelines/build.yml")
    assert bp.type == 2


def test_build_process_posix_path_coercion():
    bp = BuildProcess(yamlFilename="pipelines/build.yml")
    assert isinstance(bp.yaml_filename, PurePosixPath)


# ---------------------------------------------------------------------------
# BuildRepository
# ---------------------------------------------------------------------------


def test_build_repository_with_branch():
    repo = BuildRepository(id="repo-1", defaultBranch="refs/heads/main")
    assert repo.default_branch_name == "main"


def test_build_repository_branch_without_prefix():
    repo = BuildRepository(id="repo-1", defaultBranch="develop")
    assert repo.default_branch_name == "develop"


def test_build_repository_no_branch():
    repo = BuildRepository(id="repo-1")
    assert repo.default_branch is None
    assert repo.default_branch_name is None


def test_build_repository_refs_heads_stripped():
    repo = BuildRepository(id="r", defaultBranch="refs/heads/feature/xyz")
    assert repo.default_branch_name == "feature/xyz"


# ---------------------------------------------------------------------------
# BuildDefinitionSummary
# ---------------------------------------------------------------------------

_SUMMARY_SPEC: dict = {
    "id": 1,
    "revision": 2,
    "name": "my-build",
    "path": "\\Builds",
    "url": "https://dev.azure.com/org/proj/_apis/build/Definitions/1",
}


def test_build_definition_summary_valid():
    summary = BuildDefinitionSummary.model_validate(_SUMMARY_SPEC)
    assert summary.id == 1
    assert summary.name == "my-build"
    assert isinstance(summary.path, PureWindowsPath)


def test_build_definition_summary_with_properties():
    spec = dict(_SUMMARY_SPEC)
    spec["properties"] = {"System.ProcessTemplateType": {"$type": "System.String", "$value": "6b724908-ef14-45cf"}}
    summary = BuildDefinitionSummary.model_validate(spec)
    assert isinstance(summary.properties["System.ProcessTemplateType"], Properties)


# ---------------------------------------------------------------------------
# BuildDefinition and fullname computed property
# ---------------------------------------------------------------------------

_DEFINITION_SPEC: dict = {
    **_SUMMARY_SPEC,
    "process": {"yamlFilename": "/pipelines/build.yml"},
    "repository": {"id": "repo-abc", "defaultBranch": "refs/heads/main"},
}


def test_build_definition_fullname():
    defn = BuildDefinition.model_validate(_DEFINITION_SPEC)
    # fullname = PurePosixPath(WindowsPath('/Builds').joinpath('my-build'))
    assert defn.fullname == PurePosixPath("/Builds/my-build")


def test_build_definition_has_process_and_repository():
    defn = BuildDefinition.model_validate(_DEFINITION_SPEC)
    assert isinstance(defn.process, BuildProcess)
    assert isinstance(defn.repository, BuildRepository)


# ---------------------------------------------------------------------------
# BuildDefinitionCreate
# ---------------------------------------------------------------------------


def test_build_definition_create_valid():
    obj = BuildDefinitionCreate(
        name="new-build",
        path="\\Pipelines",
        process=BuildProcess(yamlFilename="/ci/pipeline.yml"),
        repository=BuildRepository(id="repo-1", defaultBranch="refs/heads/main"),
    )
    assert obj.name == "new-build"
    assert obj.type == "build"


def test_build_definition_create_invalid_type():
    with pytest.raises(pydantic.ValidationError):
        BuildDefinitionCreate(
            name="x",
            path="\\P",
            type="invalid",  # type: ignore[arg-type]
            process=BuildProcess(yamlFilename="/f.yml"),
            repository=BuildRepository(id="r"),
        )


# ---------------------------------------------------------------------------
# BuildDefinitionCollection
# ---------------------------------------------------------------------------

_SUMMARIES = [
    BuildDefinitionSummary.model_validate(
        {**_SUMMARY_SPEC, "id": i, "name": name, "path": path, "url": _SUMMARY_SPEC["url"]}
    )
    for i, name, path in [
        (1, "api-build", "\\Builds\\Api"),
        (2, "api-test", "\\Builds\\Api"),
        (3, "web-build", "\\Builds\\Web"),
        (4, "web-deploy", "\\Builds\\Web"),
    ]
]


def _make_collection(*items: BuildDefinitionSummary) -> BuildDefinitionCollection:
    col = BuildDefinitionCollection()
    for item in items:
        col.append(item)
    return col


@pytest.mark.parametrize(
    "pattern, expected_names",
    [
        ("api-", ["api-build", "api-test"]),
        ("web-", ["web-build", "web-deploy"]),
        ("api-build", ["api-build"]),
        ("nothing", []),
    ],
)
def test_build_definition_collection_startswith(pattern, expected_names):
    col = _make_collection(*_SUMMARIES)
    result = col.startswith(pattern)
    assert [d.name for d in result] == expected_names


@pytest.mark.parametrize(
    "pattern, expected_names",
    [
        ("Builds/Api", ["api-build", "api-test"]),
        ("Builds/Web", ["web-build", "web-deploy"]),
    ],
)
def test_build_definition_collection_from_folder(pattern, expected_names):
    col = _make_collection(*_SUMMARIES)
    result = col.from_folder(pattern)
    assert sorted(d.name for d in result) == sorted(expected_names)


def test_build_definition_collection_get_found():
    col = _make_collection(*_SUMMARIES)
    result = col.get("web-build")
    assert result is not None
    assert result.name == "web-build"


def test_build_definition_collection_get_not_found():
    col = _make_collection(*_SUMMARIES)
    assert col.get("does-not-exist") is None


# ---------------------------------------------------------------------------
# BuildClient
# ---------------------------------------------------------------------------


def test_build_client_get_build_definition(mock_session):
    mock_session.get.return_value = ok_response(_DEFINITION_SPEC)
    client = BuildClient(mock_session)

    result = client.get_build_definition("1")

    assert isinstance(result, BuildDefinition)
    assert result.name == "my-build"
    mock_session.get.assert_called_once_with("/definitions/1", params=None)


def test_build_client_list_build_definitions_no_filter(mock_session):
    payload = {"value": [_SUMMARY_SPEC]}
    mock_session.get.return_value = ok_response(payload)
    client = BuildClient(mock_session)

    result = client.list_build_definitions()

    assert isinstance(result, BuildDefinitionCollection)
    assert result.count == 1
    mock_session.get.assert_called_once_with("/definitions", params=None)


def test_build_client_list_build_definitions_with_repository(mock_session):
    repo = GitRepository.model_validate(
        {
            "id": "repo-abc",
            "name": "MyRepo",
            "project": PROJECT_SPEC,
            "defaultBranch": "refs/heads/main",
            "size": 0,
            "remoteUrl": "https://dev.azure.com/o/p/_git/r",
            "webUrl": "https://dev.azure.com/o/p/_git/r",
            "isDisabled": False,
            "isInMaintenance": False,
        }
    )
    payload = {"value": [_SUMMARY_SPEC]}
    mock_session.get.return_value = ok_response(payload)
    client = BuildClient(mock_session)

    result = client.list_build_definitions(repository=repo)

    assert result.count == 1
    call_kwargs = mock_session.get.call_args
    params = call_kwargs[1].get("params") or call_kwargs[0][1] if len(call_kwargs[0]) > 1 else call_kwargs[1]["params"]
    assert params["repositoryId"] == "repo-abc"
    assert params["repositoryType"] == "TfsGit"


def test_build_client_create_build_definition(mock_session):
    mock_session.post.return_value = ok_response(_DEFINITION_SPEC)
    client = BuildClient(mock_session)

    definition = BuildDefinitionCreate(
        name="my-build",
        path="\\Builds",
        process=BuildProcess(yamlFilename="/pipelines/build.yml"),
        repository=BuildRepository(id="repo-abc", defaultBranch="refs/heads/main"),
    )
    result = client.create_build_definition(definition)

    assert isinstance(result, BuildDefinition)
    mock_session.post.assert_called_once()


def test_build_client_delete_build_definition(mock_session):
    del_response = MagicMock()
    del_response.status_code = 204
    mock_session.delete.return_value = del_response
    client = BuildClient(mock_session)

    result = client.delete_build_definition(42)

    assert result == 204
    mock_session.delete.assert_called_once_with("/definitions/42", params=None)
