from __future__ import annotations

import copy
from typing import Any

from ipe.core.exceptions import ValidationError


def resolve_refs(spec_dict: dict[str, Any]) -> dict[str, Any]:
    resolved = copy.deepcopy(spec_dict)
    cache: dict[str, Any] = {}
    _resolve_node(resolved, resolved, set(), cache)
    return resolved


def _lookup_ref(root: dict[str, Any], ref: str) -> Any:
    if not ref.startswith("#/"):
        raise ValidationError(
            f"Unsupported $ref format: {ref}",
            "Only local JSON Pointer references (#/...) are supported",
        )

    parts = ref[2:].split("/")
    current: Any = root
    for part in parts:
        decoded = part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if decoded not in current:
                raise ValidationError(
                    f"$ref target not found: {ref}",
                    f"Component '{decoded}' does not exist in the spec",
                )
            current = current[decoded]
        else:
            raise ValidationError(
                f"$ref target not found: {ref}",
                "Reference path traverses a non-object value",
            )
    return current


def _resolve_node(
    node: Any,
    root: dict[str, Any],
    seen_refs: set[str],
    cache: dict[str, Any],
) -> Any:
    if not isinstance(node, (dict, list)):
        return node

    if isinstance(node, list):
        for i, item in enumerate(node):
            result = _resolve_node(item, root, seen_refs, cache)
            if result is not item:
                node[i] = result
        return node

    if "$ref" in node:
        return _resolve_ref(node["$ref"], root, seen_refs, cache, fallback=node)

    for key in node:
        result = _resolve_node(node[key], root, seen_refs, cache)
        if result is not node[key]:
            node[key] = result

    return node


def _resolve_ref(
    ref: str,
    root: dict[str, Any],
    seen_refs: set[str],
    cache: dict[str, Any],
    fallback: dict[str, Any],
) -> Any:
    if ref in seen_refs:
        return fallback

    if ref in cache:
        return copy.deepcopy(cache[ref])

    target = _lookup_ref(root, ref)
    if not isinstance(target, dict):
        cache[ref] = target
        return target

    seen_refs.add(ref)
    _resolve_node(target, root, seen_refs, cache)
    seen_refs.discard(ref)

    cache[ref] = target
    return copy.deepcopy(target)
