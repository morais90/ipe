import re

_CONSECUTIVE_CAPS = re.compile(r"([A-Z]+)([A-Z][a-z])")
_CAMEL_BOUNDARY = re.compile(r"([a-z0-9])([A-Z])")
_DELIMITERS = re.compile(r"[-\s.]+")
_MULTI_UNDERSCORE = re.compile(r"_+")


def to_snake_case(raw: str) -> str:
    """Convert a string to ``snake_case``.

    Parameters
    ----------
    raw : str
        The string to convert.

    Returns
    -------
    str
        The ``snake_case`` form, or an empty string when ``raw`` is empty.
    """
    if not raw:
        return ""

    result = _CONSECUTIVE_CAPS.sub(r"\1_\2", raw)
    result = _CAMEL_BOUNDARY.sub(r"\1_\2", result)
    result = _DELIMITERS.sub("_", result)
    result = _MULTI_UNDERSCORE.sub("_", result)
    return result.strip("_").lower()


def to_pascal_case(raw: str) -> str:
    """Convert a string to ``PascalCase``.

    Parameters
    ----------
    raw : str
        The string to convert.

    Returns
    -------
    str
        The ``PascalCase`` form, or an empty string when ``raw`` is empty.
    """
    if not raw:
        return ""

    return "".join(word.capitalize() for word in to_snake_case(raw).split("_") if word)
