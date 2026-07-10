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
        """Register a language target.

        Parameters
        ----------
        target : LanguageTarget
            The target to register under its own name.
        """
        self._targets[target.name] = target

    def get(self, language: str) -> LanguageTarget:
        """Look up a registered target by language name.

        Parameters
        ----------
        language : str
            The language identifier to look up.

        Returns
        -------
        LanguageTarget
            The registered target.

        Raises
        ------
        ConfigurationError
            If no target is registered for the language.
        """
        if language not in self._targets:
            available = ", ".join(sorted(self._targets)) or "none"
            raise ConfigurationError(
                f"Unknown target language: '{language}'",
                f"Available targets: {available}",
                field="target",
            )
        return self._targets[language]

    def list_languages(self) -> list[str]:
        """List the registered language names.

        Returns
        -------
        list[str]
            The registered language names, sorted.
        """
        return sorted(self._targets.keys())
