import keyword

from ipe.utils.naming import to_pascal_case, to_snake_case


def _safe_name(name: str) -> str:
    if keyword.iskeyword(name) or keyword.issoftkeyword(name):
        return name + "_"
    return name


class PythonNaming:
    def class_name(self, raw: str) -> str:
        return to_pascal_case(raw)

    def method_name(self, raw: str) -> str:
        return _safe_name(to_snake_case(raw))

    def field_name(self, raw: str) -> str:
        return _safe_name(to_snake_case(raw))

    def module_name(self, raw: str) -> str:
        return _safe_name(to_snake_case(raw))
