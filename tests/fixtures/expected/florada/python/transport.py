from __future__ import annotations

import json
from typing import Any, Protocol

import httpx
from florada_payments.exceptions import error_for_status


class Response:
    """HTTP response returned by a transport, decoupled from the HTTP library."""

    def __init__(self, status_code: int, content: bytes) -> None:
        self.status_code = status_code
        self._content = content

    def json(self) -> Any:
        return json.loads(self._content)

    def raise_for_status(self) -> None:
        if self.status_code < 400:
            return

        raise error_for_status(self.status_code, self._error_message(), self)

    def _error_message(self) -> str:
        try:
            body = self.json()
        except ValueError:
            return f"HTTP {self.status_code}"

        if not isinstance(body, dict):
            return f"HTTP {self.status_code}"

        for key in ("message", "detail", "error"):
            value = body.get(key)
            if isinstance(value, str):
                return value

        return f"HTTP {self.status_code}"


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
        params: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: httpx.Auth | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            headers=headers,
            params=params,
            cookies=cookies,
            auth=auth,
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
        httpx_response = self._client.request(
            method,
            url,
            params=params,
            json=json,
            data=data,
            files=files,
            content=content,
        )

        return Response(httpx_response.status_code, httpx_response.content)

    def close(self) -> None:
        self._client.close()


class AsyncHttpxTransport:
    """Default asynchronous transport backed by httpx."""

    def __init__(
        self,
        base_url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: httpx.Auth | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            params=params,
            cookies=cookies,
            auth=auth,
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
        httpx_response = await self._client.request(
            method,
            url,
            params=params,
            json=json,
            data=data,
            files=files,
            content=content,
        )

        return Response(httpx_response.status_code, httpx_response.content)

    async def aclose(self) -> None:
        await self._client.aclose()
