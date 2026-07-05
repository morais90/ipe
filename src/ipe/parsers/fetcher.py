from pathlib import Path
from typing import Any

import httpx
import yaml

from ipe.core.exceptions import NetworkError, ValidationError

_MAX_SPEC_BYTES = 25 * 1024 * 1024


def fetch_spec(source: str) -> dict[str, Any]:
    """Fetch and parse a spec from a file path or HTTPS URL.

    Parameters
    ----------
    source : str
        A local file path or an HTTP(S) URL.

    Returns
    -------
    dict[str, Any]
        The parsed specification document.

    Raises
    ------
    NetworkError
        If the URL cannot be fetched or is not served over HTTPS.
    ValidationError
        If the file is missing, cannot be decoded, or is not a valid
        YAML/JSON object.
    """
    if source.startswith(("https://", "http://")):
        return _fetch_url(source)
    return _fetch_file(source)


def _fetch_file(path: str) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        raise ValidationError(
            f"Spec file not found: {path}",
            "Check the file path and try again",
        )

    content = file_path.read_text()
    return _parse_content(content, source=path)


def _fetch_url(url: str) -> dict[str, Any]:
    if not url.startswith("https://"):
        raise NetworkError(
            "Only HTTPS URLs are supported",
            "Use an HTTPS URL instead",
            url=url,
        )

    try:
        content = _download(url)
    except NetworkError:
        raise
    except httpx.HTTPError as exc:
        raise NetworkError(
            f"Failed to fetch spec from {url}",
            "Check your internet connection and verify the URL",
            url=url,
        ) from exc

    return _parse_content(content, source=url)


def _download(url: str) -> str:
    with httpx.stream("GET", url, follow_redirects=True, timeout=30.0) as response:
        if not str(response.url).startswith("https://"):
            raise NetworkError(
                "Only HTTPS URLs are supported",
                "The URL redirected to a non-HTTPS location",
                url=url,
            )

        if response.status_code != 200:
            raise NetworkError(
                f"HTTP {response.status_code} when fetching spec",
                "Verify the URL points to a valid OpenAPI specification",
                url=url,
                status_code=response.status_code,
            )

        body = bytearray()
        for chunk in response.iter_bytes():
            if len(body) + len(chunk) > _MAX_SPEC_BYTES:
                limit_mb = _MAX_SPEC_BYTES // (1024 * 1024)
                raise NetworkError(
                    f"Spec exceeds the maximum size of {limit_mb} MB",
                    "Reduce the spec size or load it from a local file",
                    url=url,
                )
            body.extend(chunk)

        encoding = response.encoding or "utf-8"

    return _decode(body, encoding, url)


def _decode(body: bytes | bytearray, encoding: str, url: str) -> str:
    try:
        return body.decode(encoding)
    except UnicodeDecodeError as exc:
        raise ValidationError(
            f"Could not decode the spec from {url} as {encoding}",
            "Check the character encoding declared by the server",
        ) from exc


def _parse_content(content: str, source: str) -> dict[str, Any]:
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise ValidationError(
            f"Failed to parse spec from {source}",
            "Ensure the file is valid YAML or JSON",
        ) from exc

    if not isinstance(data, dict):
        raise ValidationError(
            f"Spec from {source} is not a valid OpenAPI document",
            "The file must contain a YAML/JSON object at the root",
        )

    return data
