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
        """Convert a raw name to a Python class name in ``PascalCase``.

        Parameters
        ----------
        raw : str
            The raw identifier to convert.

        Returns
        -------
        str
            The class name.
        """
        return to_pascal_case(raw)

    def method_name(self, raw: str) -> str:
        """Convert a raw name to a safe Python method name in ``snake_case``.

        Parameters
        ----------
        raw : str
            The raw identifier to convert.

        Returns
        -------
        str
            The method name, sanitized to a valid identifier.
        """
        return _safe_name(to_snake_case(raw))

    def field_name(self, raw: str) -> str:
        """Convert a raw name to a safe Python field name in ``snake_case``.

        Parameters
        ----------
        raw : str
            The raw identifier to convert.

        Returns
        -------
        str
            The field name, sanitized to a valid identifier.
        """
        return _safe_name(to_snake_case(raw))

    def module_name(self, raw: str) -> str:
        """Convert a raw name to a safe Python module name in ``snake_case``.

        Parameters
        ----------
        raw : str
            The raw identifier to convert.

        Returns
        -------
        str
            The module name, sanitized to a valid identifier.
        """
        return _safe_name(to_snake_case(raw))
