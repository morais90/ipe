from pathlib import Path

import pytest

from ipe.core.renderer import TemplateTreeRenderer
from ipe.targets.python.target import PythonTarget


@pytest.fixture
def template_dir(tmp_path: Path) -> Path:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    return template_dir


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    return tmp_path / "out"


def render(template_dir: Path, output_dir: Path, source: str, context: dict) -> str:
    (template_dir / "test.py.jinja").write_text(source)
    TemplateTreeRenderer(PythonTarget()).render(template_dir, output_dir, context)
    return (output_dir / "test.py").read_text()


class TestPyvalFilter:
    @pytest.mark.parametrize(
        ("value", "literal"),
        [
            (True, "True"),
            (False, "False"),
            (None, "None"),
            (42, "42"),
            (3.14, "3.14"),
            ("hello", "'hello'"),
            ([1, 2], "[1, 2]"),
        ],
    )
    def test_renders_python_literal(
        self, template_dir: Path, output_dir: Path, value: object, literal: str
    ):
        result = render(
            template_dir,
            output_dir,
            "value = {{ default | pyval }}\n",
            {"default": value},
        )

        assert result == f"value = {literal}\n"


class TestTypeImportsFilter:
    def test_uuid_and_datetime(self, template_dir: Path, output_dir: Path):
        properties = [
            {"schema_type": "string", "schema_format": "uuid"},
            {"schema_type": "string", "schema_format": "date-time"},
        ]

        result = render(
            template_dir,
            output_dir,
            "{{ properties | type_imports }}\n",
            {"properties": properties},
        )

        assert result == "from datetime import datetime\nfrom uuid import UUID\n"

    def test_object_type_imports_any(self, template_dir: Path, output_dir: Path):
        properties = [{"schema_type": "object", "schema_format": None}]

        result = render(
            template_dir,
            output_dir,
            "{{ properties | type_imports }}\n",
            {"properties": properties},
        )

        assert result == "from typing import Any\n"

    def test_no_imports_needed(self, template_dir: Path, output_dir: Path):
        properties = [{"schema_type": "string", "schema_format": None}]

        result = render(
            template_dir,
            output_dir,
            "value = {{ properties | type_imports }}",
            {"properties": properties},
        )

        assert result == "value = "


class TestParamTypeImportsFilter:
    def test_empty_when_no_typed_params(self, template_dir: Path, output_dir: Path):
        operations = [{"parameters": []}]

        result = render(
            template_dir,
            output_dir,
            "value = {{ operations | param_type_imports }}",
            {"operations": operations},
        )

        assert result == "value = "

    def test_combines_param_types(self, template_dir: Path, output_dir: Path):
        operations = [
            {
                "parameters": [
                    {"schema_type": "string", "schema_format": "uuid"},
                    {"schema_type": "string", "schema_format": "date"},
                ],
            },
        ]

        result = render(
            template_dir,
            output_dir,
            "{{ operations | param_type_imports }}\n",
            {"operations": operations},
        )

        assert result == (
            "from datetime import date\n"
            "from uuid import UUID\n"
        )


class TestSuccessResponseFilter:
    def test_picks_200_first(self, template_dir: Path, output_dir: Path):
        responses = [
            {"status_code": "404", "model_names": ["Error"]},
            {"status_code": "200", "model_names": ["Charge"]},
            {"status_code": "201", "model_names": ["Created"]},
        ]

        result = render(
            template_dir,
            output_dir,
            "{{ (responses | success_response).model_names[0] }}",
            {"responses": responses},
        )

        assert result == "Charge"

    def test_returns_none_when_no_success(self, template_dir: Path, output_dir: Path):
        responses = [{"status_code": "404", "model_names": ["Error"]}]

        result = render(
            template_dir,
            output_dir,
            "{{ (responses | success_response) or 'NONE' }}",
            {"responses": responses},
        )

        assert result == "NONE"


class TestResponseTypeFilter:
    @pytest.mark.parametrize(
        ("response", "expected"),
        [
            (None, "None"),
            ({"model_names": [], "primitive_type": None}, "None"),
            ({"model_names": [], "primitive_type": "string"}, "string"),
            ({"model_names": ["Charge"], "is_list": False}, "Charge"),
            ({"model_names": ["Charge"], "is_list": True}, "list[Charge]"),
            ({"model_names": ["A", "B"], "is_list": False}, "A | B"),
            ({"model_names": ["A", "B"], "is_list": True}, "list[A | B]"),
        ],
    )
    def test_renders_type(
        self,
        template_dir: Path,
        output_dir: Path,
        response: dict | None,
        expected: str,
    ):
        result = render(
            template_dir,
            output_dir,
            "{{ response | response_type }}",
            {"response": response},
        )

        assert result == expected


class TestResponseDeserializeFilter:
    @pytest.mark.parametrize(
        ("response", "expected"),
        [
            (None, "None"),
            ({"model_names": [], "primitive_type": "string"}, "response.json()"),
            (
                {"model_names": ["Charge"], "is_list": False},
                "Charge.model_validate(response.json())",
            ),
            (
                {"model_names": ["Charge"], "is_list": True},
                "[Charge.model_validate(item) for item in response.json()]",
            ),
            (
                {"model_names": ["A", "B"], "is_list": False},
                "TypeAdapter(A | B).validate_python(response.json())",
            ),
            (
                {
                    "model_names": ["A", "B"],
                    "discriminator": "kind",
                    "is_list": False,
                },
                'TypeAdapter(Annotated[A | B, Field(discriminator="kind")]).validate_python(response.json())',
            ),
            (
                {"model_names": ["A", "B"], "is_list": True},
                "TypeAdapter(list[A | B]).validate_python(response.json())",
            ),
        ],
    )
    def test_renders_expression(
        self,
        template_dir: Path,
        output_dir: Path,
        response: dict | None,
        expected: str,
    ):
        result = render(
            template_dir,
            output_dir,
            "{{ response | response_deserialize }}",
            {"response": response},
        )

        assert result == expected


class TestResourceImportsFilter:
    def test_combines_type_and_model_imports(
        self, template_dir: Path, output_dir: Path
    ):
        operations = [
            {
                "parameters": [
                    {"schema_type": "string", "schema_format": "uuid"},
                ],
                "responses": [
                    {"status_code": "200", "model_names": ["Charge"]},
                ],
            },
        ]

        result = render(
            template_dir,
            output_dir,
            "{{ operations | resource_imports(module_name) }}",
            {"operations": operations, "module_name": "florada_payments"},
        )

        assert result == (
            "from uuid import UUID\n"
            "\n"
            "from florada_payments.models.charge import Charge"
        )

    def test_adds_type_adapter_for_union(
        self, template_dir: Path, output_dir: Path
    ):
        operations = [
            {
                "parameters": [],
                "responses": [
                    {"status_code": "200", "model_names": ["A", "B"]},
                ],
            },
        ]

        result = render(
            template_dir,
            output_dir,
            "{{ operations | resource_imports(module_name) }}",
            {"operations": operations, "module_name": "api"},
        )

        assert result == (
            "from pydantic import TypeAdapter\n"
            "from api.models.a import A\n"
            "from api.models.b import B"
        )

    def test_adds_annotated_field_for_discriminator(
        self, template_dir: Path, output_dir: Path
    ):
        operations = [
            {
                "parameters": [],
                "responses": [
                    {
                        "status_code": "200",
                        "model_names": ["A", "B"],
                        "discriminator": "kind",
                    },
                ],
            },
        ]

        result = render(
            template_dir,
            output_dir,
            "{{ operations | resource_imports(module_name) }}",
            {"operations": operations, "module_name": "api"},
        )

        assert result == (
            "from typing import Annotated\n"
            "from pydantic import Field, TypeAdapter\n"
            "from api.models.a import A\n"
            "from api.models.b import B"
        )
