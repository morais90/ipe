import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ipe.cli.main import app

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
EXPECTED_DIR = FIXTURES_DIR / "expected"

runner = CliRunner()


class TestConfigResolution:
    def test_reads_spec_and_output_from_ipe_json(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "ipe.json").write_text(
            json.dumps(
                {
                    "spec_path": str(FIXTURES_DIR / "florada.yaml"),
                    "output_dir": "out",
                }
            )
        )

        result = runner.invoke(app, ["generate"])

        assert result.exit_code == 0
        assert (tmp_path / "out" / "client.py").exists()

    def test_cli_arguments_override_ipe_json(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "ipe.json").write_text(
            json.dumps({"spec_path": "/wrong.yaml", "output_dir": "from_config"})
        )
        spec = str(FIXTURES_DIR / "florada.yaml")

        result = runner.invoke(app, ["generate", spec, "--output", "from_cli"])

        assert result.exit_code == 0
        assert (tmp_path / "from_cli" / "client.py").exists()
        assert not (tmp_path / "from_config").exists()

    def test_missing_spec_exits_with_usage_code(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["generate"])

        assert result.exit_code == 2


class TestGenerateCommandErrors:
    def test_spec_not_found(self, tmp_path: Path):
        result = runner.invoke(
            app, ["generate", "/nonexistent.yaml", "--output", str(tmp_path)]
        )

        assert result.exit_code == 1

    def test_unknown_target(self, tmp_path: Path):
        spec = str(FIXTURES_DIR / "florada.yaml")

        result = runner.invoke(
            app, ["generate", spec, "--output", str(tmp_path), "--target", "rust"]
        )

        assert result.exit_code == 1

    def test_swagger_20_rejected(self, tmp_path: Path):
        spec = str(FIXTURES_DIR / "swagger2.yaml")

        result = runner.invoke(app, ["generate", spec, "--output", str(tmp_path)])

        assert result.exit_code == 1


@pytest.mark.parametrize(
    ("spec_name", "target", "expected_subdir"),
    [
        ("florada.yaml", "python", "florada/python"),
        ("florada-v3.0.yaml", "python", "florada/python"),
    ],
)
class TestGenerateGoldenFiles:
    def test_all_files_match_expected(
        self, tmp_path: Path, spec_name: str, target: str, expected_subdir: str
    ):
        spec = str(FIXTURES_DIR / spec_name)
        expected_dir = EXPECTED_DIR / expected_subdir

        result = runner.invoke(
            app, ["generate", spec, "--output", str(tmp_path), "--target", target]
        )

        assert result.exit_code == 0

        expected_files = sorted(
            str(f.relative_to(expected_dir)) for f in expected_dir.rglob("*.py")
        )
        generated_files = sorted(
            str(f.relative_to(tmp_path)) for f in tmp_path.rglob("*.py")
        )
        assert generated_files == expected_files

        for relative in expected_files:
            assert (tmp_path / relative).read_text() == (
                expected_dir / relative
            ).read_text()


_INLINE_BODY_SPEC = """
openapi: 3.1.0
info:
  title: Thing API
  version: "1.0"
paths:
  /things:
    post:
      operationId: createThing
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                amount:
                  $ref: '#/components/schemas/Money'
      responses:
        '201':
          description: created
components:
  schemas:
    Money:
      type: object
      properties:
        value:
          type: integer
"""

_EXPECTED_REQUEST_MODEL = """from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from thing_api.models.money import Money


class CreateThingRequest(BaseModel):
    amount: Money | None = None
"""

_EXPECTED_REQUESTS_INIT = """from __future__ import annotations

from pydantic import BaseModel

from thing_api.models import _NAMESPACE as _DOMAIN_NAMESPACE
from thing_api.models.requests.create_thing_request import CreateThingRequest

__all__: list[str] = [
    "CreateThingRequest",
]

_NAMESPACE: dict[str, type[BaseModel]] = {
    **_DOMAIN_NAMESPACE,
    "CreateThingRequest": CreateThingRequest,
}

for _model in (CreateThingRequest,):
    _model.model_rebuild(_types_namespace=_NAMESPACE)
"""


class TestRequestModelReferences:
    def _generate(self, tmp_path: Path) -> Path:
        spec = tmp_path / "thing.yaml"
        spec.write_text(_INLINE_BODY_SPEC)
        output = tmp_path / "thing_api"

        result = runner.invoke(
            app, ["generate", str(spec), "--output", str(output), "--target", "python"]
        )

        assert result.exit_code == 0
        return output

    def test_request_model_references_domain_model(self, tmp_path: Path):
        output = self._generate(tmp_path)

        request_model = output / "models" / "requests" / "create_thing_request.py"

        assert request_model.read_text() == _EXPECTED_REQUEST_MODEL

    def test_requests_init_rebuilds_only_request_models(self, tmp_path: Path):
        output = self._generate(tmp_path)

        requests_init = output / "models" / "requests" / "__init__.py"

        assert requests_init.read_text() == _EXPECTED_REQUESTS_INIT


_RECURSIVE_SPEC = """
openapi: 3.1.0
info:
  title: Recursive API
  version: "1.0"
paths:
  /trees:
    get:
      operationId: getTree
      responses:
        '200':
          description: ok
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Tree'
components:
  schemas:
    Money:
      type: object
      properties:
        value:
          type: integer
    Node:
      type: object
      properties:
        name:
          type: string
        cost:
          $ref: '#/components/schemas/Money'
        parent:
          $ref: '#/components/schemas/Tree'
    Tree:
      type: object
      properties:
        root:
          $ref: '#/components/schemas/Node'
"""

_RUNTIME_CHECK = """
from recursive_api.models.money import Money
from recursive_api.models.node import Node
from recursive_api.models.tree import Tree

tree = Tree.model_validate(
    {"root": {"name": "r", "cost": {"value": 7}, "parent": {"root": None}}}
)

assert isinstance(tree.root, Node)
assert isinstance(tree.root.cost, Money)
assert isinstance(tree.root.parent, Tree)
assert tree.root.cost.value == 7
"""


class TestGeneratedModelsResolveAtRuntime:
    def test_nested_and_recursive_models_validate(self, tmp_path: Path):
        spec = tmp_path / "recursive.yaml"
        spec.write_text(_RECURSIVE_SPEC)
        output = tmp_path / "recursive_api"

        result = runner.invoke(
            app, ["generate", str(spec), "--output", str(output), "--target", "python"]
        )

        assert result.exit_code == 0

        check = subprocess.run(
            [sys.executable, "-c", _RUNTIME_CHECK],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(tmp_path)},
            check=False,
        )

        assert check.returncode == 0, check.stderr


_CLIENT_CREDENTIALS_SPEC = """
openapi: 3.1.0
info:
  title: CC API
  version: "1.0"
paths:
  /x:
    get:
      operationId: getX
      responses:
        '200':
          description: ok
components:
  securitySchemes:
    svc:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: https://auth.example.com/token
          scopes: {}
"""

_TOKEN_FETCH_CHECK = """
import httpx
import respx
from cc_api.auth import build_auth


def make_auth():
    return build_auth(svc_client_id="cid", svc_client_secret="sec")[3]


# A valid token is fetched once, applied as Bearer, and cached across requests.
with respx.mock:
    token = respx.post("https://auth.example.com/token").mock(
        return_value=httpx.Response(200, json={"access_token": "T", "expires_in": 3600})
    )
    api = respx.get("https://api.example.com/x").mock(return_value=httpx.Response(200))

    with httpx.Client(auth=make_auth()) as client:
        client.get("https://api.example.com/x")
        client.get("https://api.example.com/x")

    assert token.call_count == 1, token.call_count
    assert b"grant_type=client_credentials" in token.calls[0].request.content
    assert api.calls[0].request.headers["Authorization"] == "Bearer T"

# A token at or under the refresh buffer is re-fetched on the next request.
with respx.mock:
    token = respx.post("https://auth.example.com/token").mock(
        return_value=httpx.Response(200, json={"access_token": "T", "expires_in": 10})
    )
    respx.get("https://api.example.com/x").mock(return_value=httpx.Response(200))

    with httpx.Client(auth=make_auth()) as client:
        client.get("https://api.example.com/x")
        client.get("https://api.example.com/x")

    assert token.call_count == 2, token.call_count

# Concurrent requests on a cold auth fetch the token once, not once each.
import threading
import time


def _slow_token(request):
    time.sleep(0.05)
    return httpx.Response(200, json={"access_token": "T", "expires_in": 3600})


with respx.mock:
    token = respx.post("https://auth.example.com/token").mock(side_effect=_slow_token)
    respx.get("https://api.example.com/x").mock(return_value=httpx.Response(200))

    with httpx.Client(auth=make_auth()) as client:
        threads = [
            threading.Thread(target=lambda: client.get("https://api.example.com/x"))
            for _ in range(5)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    assert token.call_count == 1, token.call_count

# The async client fetches the token and applies it too.
import asyncio


async def _amain():
    with respx.mock:
        token = respx.post("https://auth.example.com/token").mock(
            return_value=httpx.Response(
                200, json={"access_token": "A", "expires_in": 3600}
            )
        )
        api = respx.get("https://api.example.com/x").mock(
            return_value=httpx.Response(200)
        )

        async with httpx.AsyncClient(auth=make_auth()) as client:
            await client.get("https://api.example.com/x")
            await client.get("https://api.example.com/x")

        assert token.call_count == 1, token.call_count
        assert api.calls[0].request.headers["Authorization"] == "Bearer A"


asyncio.run(_amain())
"""


class TestClientCredentialsAuth:
    def test_token_is_fetched_and_applied(self, tmp_path: Path):
        spec = tmp_path / "cc.yaml"
        spec.write_text(_CLIENT_CREDENTIALS_SPEC)
        output = tmp_path / "cc_api"

        result = runner.invoke(
            app, ["generate", str(spec), "--output", str(output), "--target", "python"]
        )

        assert result.exit_code == 0

        check = subprocess.run(
            [sys.executable, "-c", _TOKEN_FETCH_CHECK],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(tmp_path)},
            check=False,
        )

        assert check.returncode == 0, check.stderr
