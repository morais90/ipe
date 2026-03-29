from ipe.core.exceptions import ConfigurationError
from ipe.targets.base import LanguageTarget
from ipe.targets.python.target import PythonTarget


class TargetRegistry:
    def __init__(self) -> None:
        self._targets: dict[str, LanguageTarget] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        self.register(PythonTarget())

    def register(self, target: LanguageTarget) -> None:
        self._targets[target.name] = target

    def get(self, language: str) -> LanguageTarget:
        if language not in self._targets:
            available = ", ".join(sorted(self._targets)) or "none"
            raise ConfigurationError(
                f"Unknown target language: '{language}'",
                f"Available targets: {available}",
                field="target",
            )
        return self._targets[language]

    def list_languages(self) -> list[str]:
        return sorted(self._targets.keys())
