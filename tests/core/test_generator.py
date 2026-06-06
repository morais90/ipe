from pathlib import Path

import pytest

from ipe.core.config import IpeConfig
from ipe.core.generator import CodeGenerator

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def florada_config(tmp_path: Path) -> IpeConfig:
    return IpeConfig(
        spec_path=str(FIXTURES_DIR / "florada.yaml"),
        output_dir=tmp_path,
        target="python",
    )


class TestCodeGeneratorCallbacks:
    def test_on_phase_fires_in_order(self, florada_config: IpeConfig):
        phases: list[str] = []

        CodeGenerator().run(florada_config, on_phase=phases.append)

        assert phases == [
            "Loading spec",
            "Normalizing schemas",
            "Inlining $refs",
            "Validating spec structure",
            "Indexing schemas",
            "Extracting blueprint",
            "Grouping operations",
            "Rendering templates",
        ]

    def test_on_file_fires_for_every_written_path(self, florada_config: IpeConfig):
        seen: list[Path] = []

        result = CodeGenerator().run(florada_config, on_file=seen.append)

        assert seen == result.files

    def test_result_carries_blueprint_stats(self, florada_config: IpeConfig):
        result = CodeGenerator().run(florada_config)

        assert (
            result.api_name,
            result.operations,
            result.models,
            result.resources,
        ) == ("Florada Payments", 26, 36, 11)
