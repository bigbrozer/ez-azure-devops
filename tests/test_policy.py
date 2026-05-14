"""Tests for policy models and all policy clients."""

from unittest.mock import MagicMock

from conftest import (
    POLICY_CONFIGURATION_SPEC,
    POLICY_SCOPE_SPEC,
    POLICY_SETTINGS_SPEC,
    POLICY_TYPE_SPEC,
    ok_response,
)

from ez_ados.constants import BUILD_POLICY_TYPE_ID
from ez_ados.policy.configurations.clients import GitPolicyConfigurationClient, PolicyConfigurationClient
from ez_ados.policy.configurations.models import (
    PolicyConfiguration,
    PolicyConfigurationCollection,
    PolicyConfigurationPayload,
    PolicyScope,
    PolicySettings,
)
from ez_ados.policy.types.clients import PolicyTypeClient
from ez_ados.policy.types.models import PolicyType, PolicyTypeCollection

# ---------------------------------------------------------------------------
# PolicyType model
# ---------------------------------------------------------------------------


def test_policy_type_valid(policy_type_spec):
    pt = PolicyType.model_validate(policy_type_spec)
    assert pt.id == BUILD_POLICY_TYPE_ID
    assert pt.display_name == "Build"


def test_policy_type_optional_description():
    spec = {**POLICY_TYPE_SPEC, "description": None}
    pt = PolicyType.model_validate(spec)
    assert pt.description is None


def test_policy_type_collection():
    data = {"value": [POLICY_TYPE_SPEC]}
    col = PolicyTypeCollection.model_validate(data)
    assert col.count == 1


# ---------------------------------------------------------------------------
# PolicyScope model
# ---------------------------------------------------------------------------


def test_policy_scope_valid():
    scope = PolicyScope.model_validate(POLICY_SCOPE_SPEC)
    assert scope.ref_name == "refs/heads/main"
    assert scope.match_kind == "Exact"
    assert scope.repository_id == "repo-abc"


def test_policy_scope_no_repository_id():
    scope = PolicyScope.model_validate({"refName": "refs/heads/main", "matchKind": "Exact"})
    assert scope.repository_id is None


# ---------------------------------------------------------------------------
# PolicySettings model
# ---------------------------------------------------------------------------


def test_policy_settings_valid():
    settings = PolicySettings.model_validate(POLICY_SETTINGS_SPEC)
    assert settings.display_name == "Build validation"
    assert settings.build_definition_id == 42
    assert settings.never_expire is True
    assert len(settings.scope) == 1


# ---------------------------------------------------------------------------
# PolicyConfigurationPayload model
# ---------------------------------------------------------------------------


def test_policy_configuration_payload_valid():
    spec = {
        "isEnabled": True,
        "isBlocking": True,
        "isEnterpriseManaged": False,
        "settings": POLICY_SETTINGS_SPEC,
        "type": POLICY_TYPE_SPEC,
    }
    payload = PolicyConfigurationPayload.model_validate(spec)
    assert payload.enabled is True
    assert payload.required is True
    assert isinstance(payload.type, PolicyType)


# ---------------------------------------------------------------------------
# PolicyConfiguration model
# ---------------------------------------------------------------------------


def test_policy_configuration_valid(policy_configuration_spec):
    config = PolicyConfiguration.model_validate(policy_configuration_spec)
    assert config.id == 1
    assert config.deleted is False
    assert config.settings.build_definition_id == 42


def test_policy_configuration_deleted_alias():
    spec = {**POLICY_CONFIGURATION_SPEC, "isDeleted": True}
    config = PolicyConfiguration.model_validate(spec)
    assert config.deleted is True


# ---------------------------------------------------------------------------
# PolicyConfigurationCollection
# ---------------------------------------------------------------------------

_NON_BUILD_TYPE_SPEC: dict = {
    **POLICY_CONFIGURATION_SPEC,
    "id": 2,
    "type": {
        **POLICY_TYPE_SPEC,
        "id": "some-other-type-id",
        "displayName": "Other",
    },
}

_DELETED_BUILD_SPEC: dict = {
    **POLICY_CONFIGURATION_SPEC,
    "id": 3,
    "isDeleted": True,
}

_DEF_42_SPEC: dict = POLICY_CONFIGURATION_SPEC  # buildDefinitionId == 42

_DEF_99_SPEC: dict = {
    **POLICY_CONFIGURATION_SPEC,
    "id": 4,
    "settings": {**POLICY_SETTINGS_SPEC, "buildDefinitionId": 99},
}


def _make_config_collection(*specs: dict) -> PolicyConfigurationCollection:
    col = PolicyConfigurationCollection()
    for spec in specs:
        col.append(PolicyConfiguration.model_validate(spec))
    return col


def test_policy_config_collection_get_build_policies_filters_by_type():
    col = _make_config_collection(_DEF_42_SPEC, _NON_BUILD_TYPE_SPEC)
    result = col.get_build_policies()
    assert result.count == 1
    assert result[0].type.id == BUILD_POLICY_TYPE_ID


def test_policy_config_collection_get_build_policies_skips_deleted():
    col = _make_config_collection(_DEF_42_SPEC, _DELETED_BUILD_SPEC)
    result = col.get_build_policies()
    assert result.count == 1
    assert result[0].deleted is False


def test_policy_config_collection_get_build_policies_empty():
    col = _make_config_collection(_NON_BUILD_TYPE_SPEC)
    assert col.get_build_policies().count == 0


def test_policy_config_collection_match_build_definition_hit():
    col = _make_config_collection(_DEF_42_SPEC, _DEF_99_SPEC)
    result = col.match_build_definition(42)
    assert result.count == 1
    assert result[0].settings.build_definition_id == 42


def test_policy_config_collection_match_build_definition_miss():
    col = _make_config_collection(_DEF_42_SPEC)
    assert col.match_build_definition(0).count == 0


def test_policy_config_collection_match_build_definition_skips_non_build():
    col = _make_config_collection(_NON_BUILD_TYPE_SPEC)
    assert col.match_build_definition(42).count == 0


def test_policy_config_collection_match_build_definition_skips_deleted():
    col = _make_config_collection(_DELETED_BUILD_SPEC)
    assert col.match_build_definition(42).count == 0


# ---------------------------------------------------------------------------
# PolicyConfigurationClient
# ---------------------------------------------------------------------------


def test_policy_config_client_delete(mock_session):
    del_resp = MagicMock()
    del_resp.status_code = 204
    mock_session.delete.return_value = del_resp
    client = PolicyConfigurationClient(mock_session)

    result = client.delete_policy(1)

    assert result == 204
    mock_session.delete.assert_called_once_with("1", params=None)


def test_policy_config_client_create_build_policy(mock_session, policy_configuration_spec):
    mock_session.post.return_value = ok_response(policy_configuration_spec)
    client = PolicyConfigurationClient(mock_session)

    payload = PolicyConfigurationPayload.model_validate(
        {
            "isEnabled": True,
            "isBlocking": True,
            "isEnterpriseManaged": False,
            "settings": POLICY_SETTINGS_SPEC,
            "type": POLICY_TYPE_SPEC,
        }
    )
    result = client.create_build_policy(payload)

    assert isinstance(result, PolicyConfiguration)
    mock_session.post.assert_called_once()


def test_policy_config_client_update_build_policy(mock_session, policy_configuration_spec):
    mock_session.put.return_value = ok_response(policy_configuration_spec)
    client = PolicyConfigurationClient(mock_session)

    payload = PolicyConfigurationPayload.model_validate(
        {
            "isEnabled": True,
            "isBlocking": True,
            "isEnterpriseManaged": False,
            "settings": POLICY_SETTINGS_SPEC,
            "type": POLICY_TYPE_SPEC,
        }
    )
    result = client.update_build_policy(1, payload)

    assert isinstance(result, PolicyConfiguration)
    mock_session.put.assert_called_once()
    call_args = mock_session.put.call_args
    assert call_args[0][0] == "1"


# ---------------------------------------------------------------------------
# GitPolicyConfigurationClient
# ---------------------------------------------------------------------------


def test_git_policy_client_get_policies_for_ref(mock_session, policy_configuration_spec):
    payload = {"value": [policy_configuration_spec]}
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = payload
    response.url = "https://example.com"
    response.content = b""
    mock_session.get.return_value = response
    client = GitPolicyConfigurationClient(mock_session)

    result = client.get_policies_for_ref(
        repository_id="repo-abc",
        ref_name="refs/heads/main",
        policy_type=BUILD_POLICY_TYPE_ID,
    )

    assert isinstance(result, PolicyConfigurationCollection)
    assert result.count == 1
    call_kwargs = mock_session.get.call_args[1]
    params = call_kwargs["params"]
    assert params["repositoryId"] == "repo-abc"
    assert params["refName"] == "refs/heads/main"


def test_git_policy_client_get_build_policies_for_ref(mock_session, policy_configuration_spec):
    payload = {"value": [policy_configuration_spec]}
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = payload
    response.url = "https://example.com"
    response.content = b""
    mock_session.get.return_value = response
    client = GitPolicyConfigurationClient(mock_session)

    result = client.get_build_policies_for_ref("repo-abc", "refs/heads/main")

    assert isinstance(result, PolicyConfigurationCollection)
    call_kwargs = mock_session.get.call_args[1]
    assert call_kwargs["params"]["policyType"] == BUILD_POLICY_TYPE_ID


# ---------------------------------------------------------------------------
# PolicyTypeClient
# ---------------------------------------------------------------------------


def test_policy_type_client_list(mock_session, policy_type_spec):
    payload = {"value": [policy_type_spec]}
    mock_session.get.return_value = ok_response(payload)
    client = PolicyTypeClient(mock_session)

    result = client.list()

    assert isinstance(result, PolicyTypeCollection)
    assert result.count == 1
    mock_session.get.assert_called_once_with("", params=None)


def test_policy_type_client_get(mock_session, policy_type_spec):
    mock_session.get.return_value = ok_response(policy_type_spec)
    client = PolicyTypeClient(mock_session)

    result = client.get(BUILD_POLICY_TYPE_ID)

    assert isinstance(result, PolicyType)
    assert result.id == BUILD_POLICY_TYPE_ID
    mock_session.get.assert_called_once_with(BUILD_POLICY_TYPE_ID, params=None)
