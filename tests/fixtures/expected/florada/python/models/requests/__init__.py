__all__ = []

_MODULES = {}


def __getattr__(name: str):
    """Lazy import request body schemas on first access."""
    if name not in _MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib import import_module

    module = import_module(f"{__name__}.{_MODULES[name]}")
    return getattr(module, name)
