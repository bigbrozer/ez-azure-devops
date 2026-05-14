"""Tests for pipeline models and PipelineClient."""

from pathlib import PurePosixPath, PureWindowsPath

import pydantic
import pytest

from conftest import PIPELINE_SPEC, ok_response

from ez_ados.pipelines.clients import PipelineClient
from ez_ados.pipelines.enums import ConfigurationType
from ez_ados.pipelines.models import (
    Pipeline,
    PipelineCollection,
    PipelineConfiguration,
    PipelineConfigurationRepository,
    PipelineCreate,
)

# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def test_pipeline_valid(pipeline_spec):
    p = Pipeline.model_validate(pipeline_spec)
    assert p.id == 1
    assert p.name == "my-pipeline"
    assert isinstance(p.folder, PureWindowsPath)


def test_pipeline_invalid_id():
    with pytest.raises(pydantic.ValidationError):
        Pipeline.model_validate({**PIPELINE_SPEC, "id": "not-an-int"})


# ---------------------------------------------------------------------------
# PipelineConfigurationRepository
# ---------------------------------------------------------------------------


def test_pipeline_config_repo_default_type():
    repo = PipelineConfigurationRepository(id="repo-abc")
    assert repo.type == "azureReposGit"


# ---------------------------------------------------------------------------
# PipelineConfiguration
# ---------------------------------------------------------------------------


def test_pipeline_configuration_valid():
    config = PipelineConfiguration(
        path="/pipelines/ci.yml",
        repository=PipelineConfigurationRepository(id="repo-abc"),
    )
    assert config.path == PurePosixPath("/pipelines/ci.yml")
    assert config.type == ConfigurationType.yaml


def test_pipeline_configuration_type_coercion():
    config = PipelineConfiguration(
        path="/pipelines/ci.yml",
        repository=PipelineConfigurationRepository(id="repo-abc"),
        type="yaml",
    )
    assert config.type == ConfigurationType.yaml


# ---------------------------------------------------------------------------
# PipelineCreate
# ---------------------------------------------------------------------------


def test_pipeline_create_valid():
    obj = PipelineCreate(
        name="new-pipeline",
        folder="\\Pipelines",
        configuration=PipelineConfiguration(
            path="/pipelines/ci.yml",
            repository=PipelineConfigurationRepository(id="repo-abc"),
        ),
    )
    assert obj.name == "new-pipeline"
    assert isinstance(obj.folder, PureWindowsPath)


# ---------------------------------------------------------------------------
# PipelineCollection
# ---------------------------------------------------------------------------

_PIPELINES = [
    Pipeline.model_validate({**PIPELINE_SPEC, "id": i, "name": name, "folder": folder})
    for i, name, folder in [
        (1, "api-ci", "\\CI\\Api"),
        (2, "api-cd", "\\CD\\Api"),
        (3, "web-ci", "\\CI\\Web"),
        (4, "web-cd", "\\CD\\Web"),
    ]
]


def _make_collection(*items: Pipeline) -> PipelineCollection:
    col = PipelineCollection()
    for item in items:
        col.append(item)
    return col


@pytest.mark.parametrize(
    "pattern, expected_names",
    [
        ("api-", ["api-ci", "api-cd"]),
        ("web-", ["web-ci", "web-cd"]),
        ("api-ci", ["api-ci"]),
        ("nothing", []),
    ],
)
def test_pipeline_collection_startswith(pattern, expected_names):
    col = _make_collection(*_PIPELINES)
    result = col.startswith(pattern)
    assert [p.name for p in result] == expected_names


@pytest.mark.parametrize(
    "pattern, expected_names",
    [
        ("CI/Api", ["api-ci"]),
        ("CD/Web", ["web-cd"]),
        ("CI/*", ["api-ci", "web-ci"]),
    ],
)
def test_pipeline_collection_from_folder(pattern, expected_names):
    col = _make_collection(*_PIPELINES)
    result = col.from_folder(pattern)
    assert sorted(p.name for p in result) == sorted(expected_names)


# ---------------------------------------------------------------------------
# PipelineClient
# ---------------------------------------------------------------------------


def test_pipeline_client_get(mock_session, pipeline_spec):
    mock_session.get.return_value = ok_response(pipeline_spec)
    client = PipelineClient(mock_session)

    result = client.get(1)

    assert isinstance(result, Pipeline)
    assert result.id == 1
    mock_session.get.assert_called_once_with("1", params=None)


def test_pipeline_client_list(mock_session, pipeline_spec):
    payload = {"value": [pipeline_spec]}
    mock_session.get.return_value = ok_response(payload)
    client = PipelineClient(mock_session)

    result = client.list()

    assert isinstance(result, PipelineCollection)
    assert result.count == 1
    mock_session.get.assert_called_once_with("", params=None)


def test_pipeline_client_create(mock_session, pipeline_spec):
    mock_session.post.return_value = ok_response(pipeline_spec)
    client = PipelineClient(mock_session)

    result = client.create(
        name="my-pipeline",
        folder="\\Pipelines",
        yaml_path="/pipelines/ci.yml",
        yaml_repository_id="repo-abc",
    )

    assert isinstance(result, Pipeline)
    mock_session.post.assert_called_once()
    call_kwargs = mock_session.post.call_args[1]
    body = call_kwargs["json"]
    assert body["name"] == "my-pipeline"
