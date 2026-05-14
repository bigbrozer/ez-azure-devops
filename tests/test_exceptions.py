"""Tests for the exceptions module."""

from unittest.mock import MagicMock

import niquests
import pytest

from ez_ados.exceptions import APIError, AuthenticationError, AzureDevOpsError, NotFoundError


def _http_error(status_code: int, url: str = "https://dev.azure.com/api") -> niquests.HTTPError:
    """Build a fake niquests.HTTPError with the given status code."""
    response = MagicMock()
    response.status_code = status_code
    response.text = f"Error {status_code}"
    response.request = MagicMock()
    response.request.url = url
    exc = niquests.HTTPError("error")
    exc.response = response
    return exc


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


def test_azure_devops_error_is_exception():
    assert isinstance(AzureDevOpsError("msg"), Exception)


def test_authentication_error_inherits():
    err = AuthenticationError("not authenticated")
    assert isinstance(err, AzureDevOpsError)
    assert str(err) == "not authenticated"


def test_not_found_error_inherits():
    err = NotFoundError("not found", status_code=404, url="https://example.com")
    assert isinstance(err, APIError)
    assert isinstance(err, AzureDevOpsError)


# ---------------------------------------------------------------------------
# APIError
# ---------------------------------------------------------------------------


def test_api_error_stores_fields():
    err = APIError("something went wrong", status_code=500, url="https://example.com")
    assert err.status_code == 500
    assert err.url == "https://example.com"
    assert str(err) == "something went wrong"


@pytest.mark.parametrize(
    "status_code, expected_type",
    [
        (404, NotFoundError),
        (500, APIError),
        (403, APIError),
        (400, APIError),
        (503, APIError),
    ],
)
def test_api_error_from_requests_dispatches(status_code, expected_type):
    exc = _http_error(status_code)
    result = APIError.from_requests(exc)
    assert isinstance(result, expected_type)
    assert result.status_code == status_code


def test_api_error_from_requests_message_contains_url():
    exc = _http_error(500, url="https://dev.azure.com/myorg")
    result = APIError.from_requests(exc)
    assert "https://dev.azure.com/myorg" in result.url
