
from pathlib import Path
from typing import Any

import httpx
import yaml

from ipe.core.exceptions import NetworkError, ValidationError


def fetch_spec(source: str) -> dict[str, Any]:
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
        response = httpx.get(url, follow_redirects=True, timeout=30.0)
    except httpx.HTTPError as exc:
        raise NetworkError(
            f"Failed to fetch spec from {url}",
            "Check your internet connection and verify the URL",
            url=url,
        ) from exc

    if response.status_code != 200:
        raise NetworkError(
            f"HTTP {response.status_code} when fetching spec",
            "Verify the URL points to a valid OpenAPI specification",
            url=url,
            status_code=response.status_code,
        )

    return _parse_content(response.text, source=url)


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
