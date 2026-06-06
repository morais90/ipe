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


class TestRenderOnFile:
    def test_fires_once_per_single_template(self, template_dir: Path, output_dir: Path):
        (template_dir / "a.py.jinja").write_text("a")
        (template_dir / "b.py.jinja").write_text("b")

        seen: list[Path] = []
        TemplateTreeRenderer(PythonTarget()).render(
            template_dir, output_dir, {}, on_file=seen.append
        )

        assert seen == [output_dir / "a.py", output_dir / "b.py"]

    def test_fires_once_per_repeated_item(self, template_dir: Path, output_dir: Path):
        models_dir = template_dir / "models"
        models_dir.mkdir()
        (models_dir / "{name}.py.jinja").write_text("model = '{{ model.name }}'")

        seen: list[Path] = []
        TemplateTreeRenderer(PythonTarget()).render(
            template_dir,
            output_dir,
            {"models": [{"name": "User"}, {"name": "Post"}]},
            on_file=seen.append,
        )

        assert seen == [output_dir / "models" / "user.py", output_dir / "models" / "post.py"]


class TestParamTypeImportsFilter:
    def test_always_includes_any(self, template_dir: Path, output_dir: Path):
        operations = [{"parameters": []}]

        result = render(
            template_dir,
            output_dir,
            "{{ operations | param_type_imports }}\n",
            {"operations": operations},
        )

        assert result == "from typing import Any\n"

    def test_combines_param_types_with_any(self, template_dir: Path, output_dir: Path):
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
            "from typing import Any\n"
            "from uuid import UUID\n"
        )
