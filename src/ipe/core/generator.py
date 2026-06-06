from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ipe.core.analyzer import SpecAnalyzer
from ipe.core.config import IpeConfig
from ipe.core.renderer import TemplateTreeRenderer
from ipe.targets.registry import TargetRegistry


@dataclass
class GenerationResult:
    files: list[Path]
    operations: int
    models: int
    resources: int
    api_name: str


class CodeGenerator:
    def __init__(self) -> None:
        self.analyzer = SpecAnalyzer()
        self.registry = TargetRegistry()

    def run(
        self,
        config: IpeConfig,
        on_phase: Callable[[str], None] | None = None,
        on_file: Callable[[Path], None] | None = None,
    ) -> GenerationResult:
        report = on_phase or (lambda _: None)

        spec = self.analyzer.parse(config.spec_path, on_phase=on_phase)

        report("Extracting blueprint")
        blueprint = self.analyzer.extract(spec, config)

        report("Grouping operations")
        target = self.registry.get(config.target)
        resources = target.group(blueprint.operations)

        context: dict[str, Any] = {
            **blueprint.model_dump(exclude={"operations"}),
            "resources": {
                target.naming.module_name(name): [
                    operation.model_dump() for operation in operations
                ]
                for name, operations in resources.items()
            },
        }

        report("Rendering templates")
        renderer = TemplateTreeRenderer(target)
        files = renderer.render(
            target.template_dir,
            config.output_dir,
            context,
            custom_dir=config.template_dir,
            on_file=on_file,
        )

        return GenerationResult(
            files=files,
            operations=len(blueprint.operations),
            models=len(blueprint.models),
            resources=len(resources),
            api_name=blueprint.api_name,
        )
