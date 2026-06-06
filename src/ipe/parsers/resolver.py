from collections.abc import Callable
from typing import Any

from ipe.core.exceptions import ValidationError

RefFilter = Callable[[str], bool]


def resolve_refs(
    spec_dict: dict[str, Any],
    ref_filter: RefFilter | None = None,
) -> dict[str, Any]:
    """Resolve $ref pointers in-place with shared references (no deep copy).

    Replaces each $ref dict with a direct reference to the target object.
    Cycles are broken via id-based tracking. When ``ref_filter`` is given,
    only refs for which it returns True are resolved.
    """
    resolved_ids: set[int] = set()
    _resolve_node(spec_dict, spec_dict, resolved_ids, ref_filter)
    return spec_dict


def _resolve_node(
    node: Any,
    root: dict[str, Any],
    resolved_ids: set[int],
    ref_filter: RefFilter | None,
) -> Any:
    node_id = id(node)
    if node_id in resolved_ids:
        return node
    resolved_ids.add(node_id)

    if isinstance(node, list):
        for i, item in enumerate(node):
            result = _resolve_node(item, root, resolved_ids, ref_filter)
            if result is not item:
                node[i] = result
        return node

    if not isinstance(node, dict):
        return node

    ref = node.get("$ref")
    if isinstance(ref, str) and (ref_filter is None or ref_filter(ref)):
        target = _lookup_ref(root, ref)
        return _resolve_node(target, root, resolved_ids, ref_filter)

    for key in node:
        result = _resolve_node(node[key], root, resolved_ids, ref_filter)
        if result is not node[key]:
            node[key] = result

    return node


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
