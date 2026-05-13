"""Custom exceptions for the ez_ados package."""

import httpx

HTTP_NOT_FOUND = 404


class AzureDevOpsError(Exception):
    """Base exception for all ez_ados errors."""


class AuthenticationError(AzureDevOpsError):
    """Raised when an API call is attempted before authenticating."""


class APIError(AzureDevOpsError):
    """Raised when an Azure DevOps API call returns a non-2xx response."""

    def __init__(self, message: str, status_code: int, url: str) -> None:
        """Initialize the APIError with message, status_code, and url."""
        super().__init__(message)
        self.status_code = status_code
        self.url = url

    @classmethod
    def from_httpx(cls, exc: httpx.HTTPStatusError) -> "APIError":
        """Build the most specific subclass from an httpx HTTPStatusError."""
        status_code = exc.response.status_code
        url = str(exc.request.url)
        message = f"API error {status_code} for {url}: {exc.response.text}"
        if status_code == HTTP_NOT_FOUND:
            return NotFoundError(message, status_code=status_code, url=url)
        return cls(message, status_code=status_code, url=url)


class NotFoundError(APIError):
    """Raised when an Azure DevOps resource is not found (HTTP 404)."""
