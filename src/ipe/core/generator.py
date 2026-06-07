from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ipe.core.analyzer import SpecAnalyzer
from ipe.core.config import IpeConfig
from ipe.core.formatter import Formatter
from ipe.core.renderer import TemplateTreeRenderer
from ipe.targets.base import LanguageTarget
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

        target = self.registry.get(config.target)
        formatter = self._resolve_formatter(target, config)

        if formatter is not None:
            formatter.verify()

        spec = self.analyzer.parse(config.spec_path, on_phase=on_phase)

        report("Extracting blueprint")
        blueprint = self.analyzer.extract(spec, config)

        report("Grouping operations")
        resources = target.group(blueprint.operations)

        context: dict[str, Any] = {
            **blueprint.model_dump(exclude={"operations", "body_schemas"}),
            "resources": {
                target.naming.module_name(name): [
                    operation.model_dump() for operation in operations
                ]
                for name, operations in resources.items()
            },
            "requests": [body.model_dump() for body in blueprint.body_schemas],
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

        if formatter is not None:
            report("Formatting output")
            formatter.format(config.output_dir)

        return GenerationResult(
            files=files,
            operations=len(blueprint.operations),
            models=len(blueprint.models),
            resources=len(resources),
            api_name=blueprint.api_name,
        )

    def _resolve_formatter(
        self,
        target: LanguageTarget,
        config: IpeConfig,
    ) -> Formatter | None:
        if not config.auto_format:
            return None

        formatter_config = config.formatter or target.default_formatter()

        if formatter_config is None:
            return None

        return target.make_formatter(formatter_config)
