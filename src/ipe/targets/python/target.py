from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any

from ipe.core.exceptions import IpeError
from ipe.core.formatter import Formatter, FormatterConfig
from ipe.models.standard import StandardOperation
from ipe.targets.python import auth, filters
from ipe.targets.python.formatters import RuffFormatter
from ipe.targets.python.naming import PythonNaming
from ipe.utils.grouping import by_nested_path

TYPE_MAP: dict[tuple[str, str | None], str] = {
    ("string", None): "str",
    ("string", "date-time"): "datetime",
    ("string", "date"): "date",
    ("string", "uuid"): "UUID",
    ("string", "binary"): "bytes",
    ("string", "byte"): "bytes",
    ("string", "email"): "str",
    ("string", "password"): "str",
    ("integer", None): "int",
    ("integer", "int32"): "int",
    ("integer", "int64"): "int",
    ("number", None): "float",
    ("number", "float"): "float",
    ("number", "double"): "float",
    ("boolean", None): "bool",
    ("array", None): "list",
    ("object", None): "dict[str, Any]",
}


class PythonTarget:
    def __init__(self) -> None:
        self._naming = PythonNaming()

    @property
    def name(self) -> str:
        """The target's identifier."""
        return "python"

    @property
    def naming(self) -> PythonNaming:
        """The naming convention for this target."""
        return self._naming

    def resolve_type(self, schema_type: str, schema_format: str | None) -> str:
        """Map an OpenAPI type and format to a Python type.

        Parameters
        ----------
        schema_type : str
            The OpenAPI schema type.
        schema_format : str or None
            The OpenAPI schema format, if any.

        Returns
        -------
        str
            The corresponding Python type, or ``"Any"`` when unknown.
        """
        return TYPE_MAP.get(
            (schema_type, schema_format),
            TYPE_MAP.get((schema_type, None), "Any"),
        )

    def group(
        self, operations: list[StandardOperation]
    ) -> dict[str, list[StandardOperation]]:
        """Group operations into resources by their nested path.

        Parameters
        ----------
        operations : list[StandardOperation]
            The operations to group.

        Returns
        -------
        dict[str, list[StandardOperation]]
            Operations keyed by dotted resource path.
        """
        return by_nested_path(operations)

    @property
    def template_dir(self) -> Path:
        """The root directory of this target's templates."""
        return Path(__file__).parent / "templates"

    def get_default_config(self) -> dict[str, Any]:
        """Return the target's default configuration options.

        Returns
        -------
        dict[str, Any]
            The default Python target options.
        """
        return {
            "client_library": "httpx",
            "async_support": True,
        }

    def default_formatter(self) -> FormatterConfig | None:
        """Return the target's default formatter configuration.

        Returns
        -------
        FormatterConfig or None
            The Ruff formatter configuration.
        """
        return FormatterConfig(name="ruff")

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

        Raises
        ------
        IpeError
            If the named formatter is not supported by the Python target.
        """
        builders: dict[str, Callable[[dict[str, Any]], Formatter]] = {
            "ruff": RuffFormatter,
        }

        builder = builders.get(config.name)

        if builder is None:
            raise IpeError(
                f"Python target does not support formatter '{config.name}'",
                f"Available formatters: {', '.join(sorted(builders))}",
            )

        return builder(config.options)

    def filters(self) -> dict[str, Callable[..., Any]]:
        """Return the Jinja filters this target provides.

        Returns
        -------
        dict[str, Callable[..., Any]]
            Filter functions keyed by their template name.
        """
        return {
            "resolve_type": self.resolve_type,
            "pyval": filters.pyval,
            "type_imports": partial(filters.type_imports, self),
            "model_imports": partial(filters.model_imports, self),
            "param_type_imports": partial(filters.param_type_imports, self),
            "resource_imports": partial(filters.resource_imports, self),
            "success_response": filters.success_response,
            "response_type": partial(filters.response_type, self),
            "response_deserialize": partial(filters.response_deserialize, self),
            "body_type": partial(filters.body_type, self),
            "body_call_arg": filters.body_call_arg,
            "field_type": partial(filters.field_type, self),
            "auth_params": partial(auth.auth_params, self),
            "auth_call_kwargs": partial(auth.auth_call_kwargs, self),
            "auth_apply": partial(auth.auth_apply, self),
            "auth_imports": partial(auth.auth_imports, self),
            "has_client_credentials": partial(auth.has_client_credentials, self),
        }
