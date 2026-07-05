from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol

from ipe.core.formatter import Formatter, FormatterConfig
from ipe.models.standard import StandardOperation


class NamingConvention(Protocol):
    def class_name(self, raw: str) -> str:
        """Convert a raw name to the language's class-name convention.

        Parameters
        ----------
        raw : str
            The raw identifier to convert.

        Returns
        -------
        str
            The converted class name.
        """
        ...

    def method_name(self, raw: str) -> str:
        """Convert a raw name to the language's method-name convention.

        Parameters
        ----------
        raw : str
            The raw identifier to convert.

        Returns
        -------
        str
            The converted method name.
        """
        ...

    def field_name(self, raw: str) -> str:
        """Convert a raw name to the language's field-name convention.

        Parameters
        ----------
        raw : str
            The raw identifier to convert.

        Returns
        -------
        str
            The converted field name.
        """
        ...

    def module_name(self, raw: str) -> str:
        """Convert a raw name to the language's module-name convention.

        Parameters
        ----------
        raw : str
            The raw identifier to convert.

        Returns
        -------
        str
            The converted module name.
        """
        ...


class LanguageTarget(Protocol):
    @property
    def name(self) -> str:
        """The target's identifier."""
        ...

    @property
    def naming(self) -> NamingConvention:
        """The naming convention for this target."""
        ...

    def resolve_type(self, schema_type: str, schema_format: str | None) -> str:
        """Map an OpenAPI type and format to a language type.

        Parameters
        ----------
        schema_type : str
            The OpenAPI schema type.
        schema_format : str or None
            The OpenAPI schema format, if any.

        Returns
        -------
        str
            The corresponding language type.
        """
        ...

    def group(
        self, operations: list[StandardOperation]
    ) -> dict[str, list[StandardOperation]]:
        """Group operations into resources for this target.

        Parameters
        ----------
        operations : list[StandardOperation]
            The operations to group.

        Returns
        -------
        dict[str, list[StandardOperation]]
            Operations keyed by resource name.
        """
        ...

    @property
    def template_dir(self) -> Path:
        """The root directory of this target's templates."""
        ...

    def get_default_config(self) -> dict[str, Any]:
        """Return the target's default configuration options.

        Returns
        -------
        dict[str, Any]
            The default target-specific options.
        """
        ...

    def filters(self) -> dict[str, Callable[..., Any]]:
        """Return the Jinja filters this target provides.

        Returns
        -------
        dict[str, Callable[..., Any]]
            Filter functions keyed by their template name.
        """
        ...

    def default_formatter(self) -> FormatterConfig | None:
        """Return the target's default formatter configuration.

        Returns
        -------
        FormatterConfig or None
            The default formatter, or ``None`` when the target has none.
        """
        ...

    def make_formatter(self, config: FormatterConfig) -> Formatter:
        """Build a formatter from its configuration.

        Parameters
        ----------
        config : FormatterConfig
            The formatter configuration.

        Returns
        -------
        Formatter
            The constructed formatter.
        """
        ...
