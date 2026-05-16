"""Tests for core models and ProjectClient."""

import pydantic
import pytest

from conftest import PROJECT_SPEC, error_response, ok_response

from ez_ados.core.clients import ProjectClient
from ez_ados.core.models import Project, Properties
from ez_ados.exceptions import APIError, NotFoundError

# ---------------------------------------------------------------------------
# Project model
# ---------------------------------------------------------------------------


def test_project_valid():
    proj = Project.model_validate(PROJECT_SPEC)
    assert proj.id == "abc-123"
    assert proj.name == "MyProject"


def test_project_validate_by_name():
    proj = Project(id="x", name="Y")
    assert proj.id == "x"


def test_project_invalid_id_type():
    with pytest.raises(pydantic.ValidationError):
        Project(id=123, name="bad")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Properties model
# ---------------------------------------------------------------------------


def test_properties_aliased_fields():
    props = Properties.model_validate({"$type": "System.String", "$value": "hello"})
    assert props.type == "System.String"
    assert props.value == "hello"


def test_properties_type_none():
    props = Properties.model_validate({"$value": 42})
    assert props.type is None
    assert props.value == 42


def test_properties_value_any_type():
    props = Properties.model_validate({"$type": "System.Int32", "$value": 99})
    assert props.value == 99


# ---------------------------------------------------------------------------
# ProjectClient
# ---------------------------------------------------------------------------


def test_project_client_get(mock_session):
    mock_session.get.return_value = ok_response(PROJECT_SPEC)
    client = ProjectClient(mock_session)

    result = client.get("MyProject")

    assert isinstance(result, Project)
    assert result.id == "abc-123"
    mock_session.get.assert_called_once_with("MyProject", params=None)


def test_project_client_get_raises_on_http_error(mock_session):
    mock_session.get.return_value = error_response(500)
    client = ProjectClient(mock_session)

    with pytest.raises(APIError):
        client.get("NonExistent")


def test_project_client_get_raises_not_found(mock_session):
    mock_session.get.return_value = error_response(404)
    client = ProjectClient(mock_session)

    with pytest.raises(NotFoundError):
        client.get("Ghost")
