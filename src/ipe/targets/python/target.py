from typing import Any

from ipe.models.standard import StandardOperation
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
        return "python"

    @property
    def naming(self) -> PythonNaming:
        return self._naming

    def resolve_type(self, schema_type: str, schema_format: str | None) -> str:
        return TYPE_MAP.get(
            (schema_type, schema_format),
            TYPE_MAP.get((schema_type, None), "Any"),
        )

    def group(
        self, operations: list[StandardOperation]
    ) -> dict[str, list[StandardOperation]]:
        return by_nested_path(operations)

    def get_default_config(self) -> dict[str, Any]:
        return {
            "client_library": "httpx",
            "async_support": True,
        }
