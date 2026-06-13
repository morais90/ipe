from pathlib import Path

import pytest
from typer.testing import CliRunner

from ipe.cli.main import app

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
EXPECTED_DIR = FIXTURES_DIR / "expected"

runner = CliRunner()


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
