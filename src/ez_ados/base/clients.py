"""Base classes for instantiating clients."""

import httpx


class Client:
    """Base class for a client."""

    def __init__(self, client: httpx.Client):
        """Instantiate a new client."""
        self._client = client
        self.base_url = self._client.base_url

    def close(self) -> None:
        """Close client connection."""
        self._client.close()
