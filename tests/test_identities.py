"""Tests for identity models and IdentityClient."""

import pytest

from conftest import IDENTITY_SPEC, ok_response

from ez_ados.identities.clients import IdentityClient
from ez_ados.identities.models import Identity, IdentityCollection

# ---------------------------------------------------------------------------
# Identity model
# ---------------------------------------------------------------------------


def test_identity_valid(identity_spec):
    identity = Identity.model_validate(identity_spec)
    assert identity.id == "user-id-123"
    assert identity.provider_display_name == "John Doe"
    assert identity.is_active is True
    assert identity.descriptor == "bnd;abc"
    assert identity.subject_descriptor == "vssgp.abc"


def test_identity_optional_fields_default_none():
    identity = Identity.model_validate({"id": "x"})
    assert identity.provider_display_name is None
    assert identity.is_active is None
    assert identity.descriptor is None


def test_identity_model_dump_round_trip(identity_spec):
    identity = Identity.model_validate(identity_spec)
    dumped = identity.model_dump(exclude_none=True)
    assert dumped["id"] == "user-id-123"


def test_identity_collection():
    data = {"value": [IDENTITY_SPEC, {**IDENTITY_SPEC, "id": "user-id-456"}]}
    col = IdentityCollection.model_validate(data)
    assert col.count == 2
    assert col[0].id == "user-id-123"
    assert col[1].id == "user-id-456"


# ---------------------------------------------------------------------------
# IdentityClient
# ---------------------------------------------------------------------------


def test_identity_client_search_by_email(mock_session):
    payload = {"value": [IDENTITY_SPEC]}
    mock_session.get.return_value = ok_response(payload)
    client = IdentityClient(mock_session)

    result = client.search_by_email("john@example.com")

    assert isinstance(result, IdentityCollection)
    assert result.count == 1
    call_kwargs = mock_session.get.call_args
    params = call_kwargs[1].get("params") or {}
    assert params.get("filterValue") == "john@example.com"
    assert params.get("searchFilter") == "General"


def test_identity_client_resolve_identities_by_email_success(mock_session):
    payload = {"value": [IDENTITY_SPEC]}
    mock_session.get.return_value = ok_response(payload)
    client = IdentityClient(mock_session)

    result = client.resolve_identities_by_email(["john@example.com"])

    assert len(result) == 1
    assert isinstance(result[0], Identity)
    assert result[0].id == "user-id-123"


def test_identity_client_resolve_identities_multiple_emails(mock_session):
    spec2 = {**IDENTITY_SPEC, "id": "user-id-456", "providerDisplayName": "Jane Doe"}
    responses = [
        ok_response({"value": [IDENTITY_SPEC]}),
        ok_response({"value": [spec2]}),
    ]
    mock_session.get.side_effect = responses
    client = IdentityClient(mock_session)

    result = client.resolve_identities_by_email(["john@example.com", "jane@example.com"])

    assert len(result) == 2
    assert result[0].id == "user-id-123"
    assert result[1].id == "user-id-456"


def test_identity_client_resolve_identities_unresolved_raises(mock_session):
    mock_session.get.return_value = ok_response({"value": []})
    client = IdentityClient(mock_session)

    with pytest.raises(ValueError, match="unknown@example.com"):
        client.resolve_identities_by_email(["unknown@example.com"])


def test_identity_client_resolve_identities_partial_failure(mock_session):
    responses = [
        ok_response({"value": [IDENTITY_SPEC]}),
        ok_response({"value": []}),
    ]
    mock_session.get.side_effect = responses
    client = IdentityClient(mock_session)

    with pytest.raises(ValueError):
        client.resolve_identities_by_email(["john@example.com", "ghost@example.com"])
