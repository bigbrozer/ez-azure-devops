"""Base classes for instantiating clients."""

from typing import Any, TypeVar

import niquests

from pydantic import BaseModel

from ..exceptions import APIError  # noqa: TCH001

M = TypeVar("M", bound=BaseModel)


class Client:
    """Base class for a client."""

    def __init__(self, client: niquests.Session):
        """Instantiate a new client."""
        self._client = client
        self.base_url = self._client.base_url

    def close(self) -> None:
        """Close client connection."""
        self._client.close()

    @staticmethod
    def _raise_for_status(response: niquests.Response) -> niquests.Response:
        """Raise a typed APIError instead of a raw niquests exception."""
        try:
            response.raise_for_status()
        except niquests.HTTPError as exc:
            raise APIError.from_requests(exc) from exc
        return response

    def _get_resource(self, url: str, model: type[M], **params: Any) -> M:
        """Perform a GET request and return a validated model instance."""
        response = self._raise_for_status(self._client.get(url, params=params or None))
        return model.model_validate(response.json())

    def _post_resource(self, url: str, model: type[M], body: dict[str, Any], **params: Any) -> M:
        """Perform a POST request and return a validated model instance."""
        response = self._raise_for_status(self._client.post(url, json=body, params=params or None))
        return model.model_validate(response.json())

    def _put_resource(self, url: str, model: type[M], body: dict[str, Any], **params: Any) -> M:
        """Perform a PUT request and return a validated model instance."""
        response = self._raise_for_status(self._client.put(url, json=body, params=params or None))
        return model.model_validate(response.json())

    def _delete_resource(self, url: str, **params: Any) -> int:
        """Perform a DELETE request and return the HTTP status code."""
        response = self._raise_for_status(self._client.delete(url, params=params or None))
        assert response.status_code is not None  # noqa: S101
        return response.status_code
