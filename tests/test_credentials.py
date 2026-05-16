"""Tests for the credentials module (AccessTokenCredential; Azure/SP skipped)."""

import pytest

from ez_ados.credentials import AccessTokenCredential, TokenCredential


def test_token_credential_get_token_raises_not_implemented():
    cred = TokenCredential()
    with pytest.raises(NotImplementedError):
        cred.get_token()


def test_access_token_credential_stores_token():
    cred = AccessTokenCredential("my-token-value")
    assert cred.token == "my-token-value"


def test_access_token_credential_get_token_returns_stored_token():
    token = "bearer-xyz-123"
    cred = AccessTokenCredential(token)
    assert cred.get_token() == token


def test_access_token_credential_is_token_credential():
    cred = AccessTokenCredential("x")
    assert isinstance(cred, TokenCredential)
