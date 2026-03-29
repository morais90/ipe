"""Swagger Petstore API client."""

from __future__ import annotations

import httpx

from swagger_petstore.resources.pets import PetsResource


class SwaggerPetstoreClient:
    """Client for the Swagger Petstore API.

    Usage:
        client = SwaggerPetstoreClient(base_url="http://petstore.swagger.io/v1")
        client.pets.list()
    """

    def __init__(
        self,
        base_url: str = "http://petstore.swagger.io/v1",
        *,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
        )
        if api_key:
            self._client.headers["Authorization"] = f"Bearer {api_key}"

        self.pets = PetsResource(self._client)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> SwaggerPetstoreClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
