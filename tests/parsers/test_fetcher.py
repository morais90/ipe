from pathlib import Path

import httpx
import pytest
import respx

from ipe.core.exceptions import NetworkError, ValidationError
from ipe.parsers.fetcher import fetch_spec

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestFetchFromFile:
    def test_load_yaml(self):
        result = fetch_spec(str(FIXTURES_DIR / "florada.yaml"))

        assert result["openapi"] == "3.1.0"
        assert result["info"]["title"] == "Florada Payments"

    def test_load_v30(self):
        result = fetch_spec(str(FIXTURES_DIR / "florada-v3.0.yaml"))

        assert result["openapi"] == "3.0.3"
        assert result["info"]["title"] == "Florada Payments"

    def test_file_not_found(self):
        with pytest.raises(ValidationError, match="not found"):
            fetch_spec("/nonexistent/path/spec.yaml")

    def test_invalid_yaml(self, tmp_path: Path):
        bad_file = tmp_path / "broken.yaml"
        bad_file.write_text(": :\n  - [unterminated")

        with pytest.raises(ValidationError, match="Failed to parse"):
            fetch_spec(str(bad_file))

    def test_json_file(self, tmp_path: Path):
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(
            '{"openapi": "3.0.0", "info": {"title": "T", "version": "1"}, "paths": {}}'
        )

        result = fetch_spec(str(spec_file))

        assert result == {
            "openapi": "3.0.0",
            "info": {"title": "T", "version": "1"},
            "paths": {},
        }

    def test_non_object_content(self, tmp_path: Path):
        spec_file = tmp_path / "list.yaml"
        spec_file.write_text("- item1\n- item2\n")

        with pytest.raises(ValidationError, match="not a valid OpenAPI document"):
            fetch_spec(str(spec_file))


class TestFetchFromURL:
    @respx.mock
    def test_fetch_https(self):
        respx.get("https://example.com/spec.yaml").mock(
            return_value=httpx.Response(
                200,
                text='openapi: "3.0.0"\ninfo:\n  title: Remote\n  version: "1.0"\npaths: {}',
            )
        )

        result = fetch_spec("https://example.com/spec.yaml")

        assert result == {
            "openapi": "3.0.0",
            "info": {"title": "Remote", "version": "1.0"},
            "paths": {},
        }

    def test_reject_http(self):
        with pytest.raises(NetworkError, match="Only HTTPS"):
            fetch_spec("http://example.com/spec.yaml")

    @respx.mock
    def test_http_404(self):
        respx.get("https://example.com/missing.yaml").mock(
            return_value=httpx.Response(404)
        )

        with pytest.raises(NetworkError, match="404"):
            fetch_spec("https://example.com/missing.yaml")

    @respx.mock
    def test_connection_error(self):
        respx.get("https://unreachable.example.com/spec.yaml").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with pytest.raises(NetworkError, match="Failed to fetch"):
            fetch_spec("https://unreachable.example.com/spec.yaml")

    @respx.mock
    def test_invalid_yaml_from_url(self):
        respx.get("https://example.com/bad.yaml").mock(
            return_value=httpx.Response(200, text=": :\n  - [invalid")
        )

        with pytest.raises(ValidationError, match="Failed to parse"):
            fetch_spec("https://example.com/bad.yaml")
