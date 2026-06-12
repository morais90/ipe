from __future__ import annotations

from typing import Any, Protocol

import httpx


class Response(Protocol):
    """Normalized HTTP response consumed by resources."""

    def json(self) -> Any: ...

    def raise_for_status(self) -> object: ...


class Transport(Protocol):
    """Synchronous HTTP transport contract.

    Implement this to back the client with an HTTP library other than the
    bundled httpx default.
    """

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        content: Any = None,
    ) -> Response: ...

    def close(self) -> None: ...


class AsyncTransport(Protocol):
    """Asynchronous HTTP transport contract."""

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        content: Any = None,
    ) -> Response: ...

    async def aclose(self) -> None: ...


class HttpxTransport:
    """Default synchronous transport backed by httpx."""

    def __init__(
        self,
        base_url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        content: Any = None,
    ) -> Response:
        return self._client.request(
            method,
            url,
            params=params,
            json=json,
            data=data,
            files=files,
            content=content,
        )

    def close(self) -> None:
        self._client.close()


class AsyncHttpxTransport:
    """Default asynchronous transport backed by httpx."""

    def __init__(
        self,
        base_url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        content: Any = None,
    ) -> Response:
        return await self._client.request(
            method,
            url,
            params=params,
            json=json,
            data=data,
            files=files,
            content=content,
        )

    async def aclose(self) -> None:
        await self._client.aclose()
