from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ipe.models.standard import StandardOperation

ROOT_RESOURCE = "root"


def by_tag(
    operations: list[StandardOperation],
) -> dict[str, list[StandardOperation]]:
    """Group operations by their first tag, falling back to the path.

    Parameters
    ----------
    operations : list[StandardOperation]
        The operations to group.

    Returns
    -------
    dict[str, list[StandardOperation]]
        Operations keyed by resource name.
    """

    def key(operation: StandardOperation) -> str:
        if operation.tags:
            return operation.tags[0].lower()
        return _resource_from_path(operation.path)

    return _group_by(operations, key)


def by_path(
    operations: list[StandardOperation],
) -> dict[str, list[StandardOperation]]:
    """Group operations by the first segment of their path.

    Parameters
    ----------
    operations : list[StandardOperation]
        The operations to group.

    Returns
    -------
    dict[str, list[StandardOperation]]
        Operations keyed by resource name.
    """
    return _group_by(operations, lambda operation: _resource_from_path(operation.path))


def by_nested_path(
    operations: list[StandardOperation],
) -> dict[str, list[StandardOperation]]:
    """Group operations by their full nested path.

    Parameters
    ----------
    operations : list[StandardOperation]
        The operations to group.

    Returns
    -------
    dict[str, list[StandardOperation]]
        Operations keyed by dotted resource path.
    """
    return _group_by(
        operations, lambda operation: _nested_resource_from_path(operation.path)
    )


def _group_by(
    operations: list[StandardOperation],
    key: Callable[[StandardOperation], str],
) -> dict[str, list[StandardOperation]]:
    groups: dict[str, list[StandardOperation]] = {}
    for operation in operations:
        groups.setdefault(key(operation), []).append(operation)
    return groups


def _path_segments(path: str) -> list[str]:
    return [s for s in path.split("/") if s and not s.startswith("{")]


def _resource_from_path(path: str) -> str:
    segments = _path_segments(path)
    return segments[0] if segments else ROOT_RESOURCE


def _nested_resource_from_path(path: str) -> str:
    segments = _path_segments(path)
    return ".".join(segments) if segments else ROOT_RESOURCE
