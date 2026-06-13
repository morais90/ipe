from pathlib import Path

import httpx
import pytest
import respx

from ipe.core.exceptions import NetworkError, ValidationError
from ipe.parsers.fetcher import fetch_spec

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

_REMOTE_SPEC = 'openapi: "3.0.0"\ninfo:\n  title: T\n  version: "1"\npaths: {}\n'


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

    @respx.mock
    def test_rejects_response_over_limit(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("ipe.parsers.fetcher._MAX_SPEC_BYTES", 16)
        respx.get("https://example.com/huge.yaml").mock(
            return_value=httpx.Response(200, text="x" * 1024)
        )

        with pytest.raises(NetworkError, match="maximum size"):
            fetch_spec("https://example.com/huge.yaml")

    @respx.mock
    def test_size_limit_message_reports_megabytes(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr("ipe.parsers.fetcher._MAX_SPEC_BYTES", 2 * 1024 * 1024)
        respx.get("https://example.com/big.yaml").mock(
            return_value=httpx.Response(200, text="x" * (2 * 1024 * 1024 + 1))
        )

        with pytest.raises(NetworkError, match="2 MB"):
            fetch_spec("https://example.com/big.yaml")

    @respx.mock
    def test_rejects_cumulative_size_across_chunks(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr("ipe.parsers.fetcher._MAX_SPEC_BYTES", 20)
        respx.get("https://example.com/chunked.yaml").mock(
            return_value=httpx.Response(
                200, content=iter([b"x" * 8, b"x" * 8, b"x" * 8])
            )
        )

        with pytest.raises(NetworkError, match="maximum size"):
            fetch_spec("https://example.com/chunked.yaml")

    @respx.mock
    def test_accepts_response_at_exact_limit(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "ipe.parsers.fetcher._MAX_SPEC_BYTES", len(_REMOTE_SPEC.encode())
        )
        respx.get("https://example.com/exact.yaml").mock(
            return_value=httpx.Response(200, text=_REMOTE_SPEC)
        )

        result = fetch_spec("https://example.com/exact.yaml")

        assert result["openapi"] == "3.0.0"

    @respx.mock
    def test_rejects_response_one_byte_over_limit(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(
            "ipe.parsers.fetcher._MAX_SPEC_BYTES", len(_REMOTE_SPEC.encode()) - 1
        )
        respx.get("https://example.com/over.yaml").mock(
            return_value=httpx.Response(200, text=_REMOTE_SPEC)
        )

        with pytest.raises(NetworkError, match="maximum size"):
            fetch_spec("https://example.com/over.yaml")

    @respx.mock
    def test_rejects_redirect_to_http(self):
        respx.get("https://example.com/spec.yaml").mock(
            return_value=httpx.Response(
                302, headers={"Location": "http://evil.example.com/spec.yaml"}
            )
        )
        respx.get("http://evil.example.com/spec.yaml").mock(
            return_value=httpx.Response(200, text=_REMOTE_SPEC)
        )

        with pytest.raises(NetworkError, match="Only HTTPS"):
            fetch_spec("https://example.com/spec.yaml")

    @respx.mock
    def test_undecodable_body_raises_validation_error(self):
        respx.get("https://example.com/binary.yaml").mock(
            return_value=httpx.Response(
                200,
                headers={"Content-Type": "text/plain; charset=utf-8"},
                content=b"\xff\xfe\x00bad",
            )
        )

        with pytest.raises(ValidationError, match="Could not decode"):
            fetch_spec("https://example.com/binary.yaml")

    @respx.mock
    def test_honors_declared_non_utf8_encoding(self):
        body = 'openapi: "3.0.0"\ninfo:\n  title: café\n  version: "1"\npaths: {}\n'

        respx.get("https://example.com/latin1.yaml").mock(
            return_value=httpx.Response(
                200,
                headers={"Content-Type": "text/yaml; charset=latin-1"},
                content=body.encode("latin-1"),
            )
        )

        result = fetch_spec("https://example.com/latin1.yaml")

        assert result["info"]["title"] == "café"
