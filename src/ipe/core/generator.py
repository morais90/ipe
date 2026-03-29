from pathlib import Path
from typing import Any

from ipe.core.analyzer import SpecAnalyzer
from ipe.core.config import IpeConfig
from ipe.core.renderer import TemplateTreeRenderer
from ipe.targets.registry import TargetRegistry


class CodeGenerator:
    def __init__(self) -> None:
        self.analyzer = SpecAnalyzer()
        self.registry = TargetRegistry()

    def run(self, config: IpeConfig) -> list[Path]:
        spec = self.analyzer.parse(config.spec_path)
        blueprint = self.analyzer.extract(spec, config)
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

        renderer = TemplateTreeRenderer(target)
        return renderer.render(
            target.template_dir,
            config.output_dir,
            context,
            custom_dir=config.template_dir,
        )
