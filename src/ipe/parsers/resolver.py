from typing import Any

from ipe.core.exceptions import ValidationError


def resolve_refs(spec_dict: dict[str, Any]) -> dict[str, Any]:
    """Resolve $ref pointers in-place with shared references (no deep copy).

    Replaces each $ref dict with a direct reference to the target object.
    Does NOT recurse into resolved targets — avoids infinite loops on
    circular refs and keeps resolution O(nodes) for large specs.
    """
    resolved_ids: set[int] = set()
    _resolve_node(spec_dict, spec_dict, resolved_ids)
    return spec_dict


def _resolve_node(
    node: Any,
    root: dict[str, Any],
    resolved_ids: set[int],
) -> Any:
    node_id = id(node)
    if node_id in resolved_ids:
        return node
    resolved_ids.add(node_id)

    if isinstance(node, list):
        for i, item in enumerate(node):
            result = _resolve_node(item, root, resolved_ids)
            if result is not item:
                node[i] = result
        return node

    if not isinstance(node, dict):
        return node

    if "$ref" in node:
        return _lookup_ref(root, node["$ref"])

    for key in node:
        result = _resolve_node(node[key], root, resolved_ids)
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
