import keyword
import re

from ipe.utils.naming import to_pascal_case, to_snake_case

_NON_IDENTIFIER = re.compile(r"[^0-9a-zA-Z_]")


def _safe_name(name: str) -> str:
    cleaned = _NON_IDENTIFIER.sub("_", name)

    if not cleaned or cleaned[0].isdigit():
        cleaned = f"_{cleaned}"

    if keyword.iskeyword(cleaned) or keyword.issoftkeyword(cleaned):
        return f"{cleaned}_"

    return cleaned


class PythonNaming:
    def class_name(self, raw: str) -> str:
        return to_pascal_case(raw)

    def method_name(self, raw: str) -> str:
        return _safe_name(to_snake_case(raw))

    def field_name(self, raw: str) -> str:
        return _safe_name(to_snake_case(raw))

    def module_name(self, raw: str) -> str:
        return _safe_name(to_snake_case(raw))
