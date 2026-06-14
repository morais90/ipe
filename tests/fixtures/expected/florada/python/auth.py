from __future__ import annotations


def build_auth(
    *,
    bearer_auth: str | None = None,
    api_key_auth: str | None = None,
    oauth2: str | None = None,
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    headers: dict[str, str] = {}
    params: dict[str, str] = {}
    cookies: dict[str, str] = {}

    if bearer_auth is not None:
        headers["Authorization"] = f"Bearer {bearer_auth}"
    if api_key_auth is not None:
        headers["X-Florada-Key"] = api_key_auth
    if oauth2 is not None:
        headers["Authorization"] = f"Bearer {oauth2}"

    return headers, params, cookies
