from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import AsyncGenerator, Generator

import httpx


class OAuth2ClientCredentials(httpx.Auth):
    def __init__(self, token_url: str, client_id: str, client_secret: str) -> None:
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._token: str | None = None
        self._expires_at = 0.0
        self._sync_lock = threading.Lock()
        self._async_lock = asyncio.Lock()

    def _is_fresh(self) -> bool:
        return self._token is not None and time.monotonic() < self._expires_at

    def _token_request(self) -> httpx.Request:
        return httpx.Request(
            "POST",
            self._token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        )

    def _store(self, response: httpx.Response) -> None:
        response.raise_for_status()
        payload = response.json()
        self._token = payload["access_token"]
        self._expires_at = time.monotonic() + payload.get("expires_in", 3600) - 60

    def sync_auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        if not self._is_fresh():
            with self._sync_lock:
                if not self._is_fresh():
                    response = yield self._token_request()
                    response.read()
                    self._store(response)

        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        if not self._is_fresh():
            async with self._async_lock:
                if not self._is_fresh():
                    response = yield self._token_request()
                    await response.aread()
                    self._store(response)

        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request


def build_auth(
    *,
    bearer_auth: str | None = None,
    api_key_auth: str | None = None,
    oauth2_client_id: str | None = None,
    oauth2_client_secret: str | None = None,
) -> tuple[dict[str, str], dict[str, str], dict[str, str], httpx.Auth | None]:
    headers: dict[str, str] = {}
    params: dict[str, str] = {}
    cookies: dict[str, str] = {}
    auth: httpx.Auth | None = None

    if bearer_auth is not None:
        headers["Authorization"] = f"Bearer {bearer_auth}"
    if api_key_auth is not None:
        headers["X-Florada-Key"] = api_key_auth
    if oauth2_client_id is not None and oauth2_client_secret is not None:
        auth = OAuth2ClientCredentials(
            "https://auth.florada.dev/oauth/token",
            oauth2_client_id,
            oauth2_client_secret,
        )

    return headers, params, cookies, auth
