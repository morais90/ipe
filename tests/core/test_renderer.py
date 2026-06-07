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
