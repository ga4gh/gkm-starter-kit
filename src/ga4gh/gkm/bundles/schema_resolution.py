"""Schema traversal used to materialize bundle-local pointer targets."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


def schema_for_pointer(
    schema: Mapping[str, Any], parts: list[str]
) -> Mapping[str, Any] | None:
    """Return the producer-schema node that describes a JSON Pointer target.

    :param schema: Root producer JSON Schema.
    :param parts: Decoded JSON Pointer path segments.
    :return: The target schema node, or ``None`` when it cannot be determined.
    """
    candidates: list[Mapping[str, Any]] = [schema]

    for part in parts:
        candidates = [
            child
            for candidate in candidates
            for child in _schema_children(candidate, part, schema)
        ]
        if not candidates:
            return None

    return candidates[0]


def _schema_children(
    schema: Mapping[str, Any], part: str, root: Mapping[str, Any]
) -> list[Mapping[str, Any]]:
    """Return all schemas applicable to one JSON Pointer path segment.

    :param schema: Schema node from which to traverse.
    :param part: Decoded JSON Pointer path segment.
    :param root: Root producer JSON Schema.
    :return: Applicable child schema nodes.
    """
    resolved = _resolve_local_reference(schema, root)
    if resolved is not schema:
        return _schema_children(resolved, part, root)

    children, matched_property = _object_schema_children(schema, part)
    children.extend(_array_schema_children(schema, part))
    children.extend(_composed_schema_children(schema, part, root))

    if not matched_property:
        additional = schema.get("additionalProperties")
        if isinstance(additional, Mapping):
            children.append(additional)

    return children


def _object_schema_children(
    schema: Mapping[str, Any], part: str
) -> tuple[list[Mapping[str, Any]], bool]:
    """Return schemas for an object property and whether it matched explicitly.

    :param schema: Object schema to inspect.
    :param part: Decoded JSON Pointer property name.
    :return: Matching child schemas and whether a named schema matched.
    """
    children: list[Mapping[str, Any]] = []
    properties = schema.get("properties")
    if isinstance(properties, Mapping) and isinstance(properties.get(part), Mapping):
        children.append(properties[part])

    patterns = schema.get("patternProperties")
    if isinstance(patterns, Mapping):
        for pattern, child in patterns.items():
            if _matches_pattern_property(pattern, child, part):
                children.append(child)

    return children, bool(children)


def _matches_pattern_property(pattern: object, child: object, part: str) -> bool:
    """Return whether a JSON Schema pattern property applies to ``part``.

    :param pattern: Candidate JSON Schema regular-expression pattern.
    :param child: Candidate schema associated with the pattern.
    :param part: Decoded JSON Pointer property name.
    :return: ``True`` when the pattern is valid and applies to the property.
    """
    if not isinstance(pattern, str) or not isinstance(child, Mapping):
        return False

    try:
        return re.search(pattern, part) is not None
    except re.error:
        return False


def _array_schema_children(
    schema: Mapping[str, Any], part: str
) -> list[Mapping[str, Any]]:
    """Return the item schema selected by a numeric JSON Pointer segment.

    :param schema: Array schema to inspect.
    :param part: Decoded JSON Pointer path segment.
    :return: The selected item schema, if any.
    """
    if not part.isdigit():
        return []

    index = int(part)
    prefix_items = schema.get("prefixItems")
    if isinstance(prefix_items, list) and index < len(prefix_items):
        item = prefix_items[index]
        return [item] if isinstance(item, Mapping) else []

    items = schema.get("items")
    return [items] if isinstance(items, Mapping) else []


def _composed_schema_children(
    schema: Mapping[str, Any], part: str, root: Mapping[str, Any]
) -> list[Mapping[str, Any]]:
    """Return child schemas contributed by ``allOf`` composition branches.

    :param schema: Schema whose composition branches to inspect.
    :param part: Decoded JSON Pointer path segment.
    :param root: Root producer JSON Schema.
    :return: Applicable child schemas from every ``allOf`` branch.
    """
    return [
        child
        for branch in schema.get("allOf", [])
        if isinstance(branch, Mapping)
        for child in _schema_children(branch, part, root)
    ]


def _resolve_local_reference(
    schema: Mapping[str, Any], root: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Resolve one local ``$ref`` against the producer schema root.

    :param schema: Schema node that may contain a local reference.
    :param root: Root producer JSON Schema.
    :return: The referenced schema, or the original schema when unresolved.
    """
    reference = schema.get("$ref")
    if not isinstance(reference, str) or not reference.startswith("#/"):
        return schema

    value: Any = root
    for raw_part in reference[2:].split("/"):
        if not isinstance(value, Mapping):
            return schema

        value = value.get(raw_part.replace("~1", "/").replace("~0", "~"))

    return value if isinstance(value, Mapping) else schema


def schema_references(
    schema: Mapping[str, Any], root: Mapping[str, Any]
) -> tuple[str, ...]:
    """Return external references identified by a target producer-schema node.

    :param schema: Schema node for the resolved pointer target.
    :param root: Root producer JSON Schema used to resolve local references.
    :return: External schema references, in schema order.
    """
    resolved = _resolve_local_reference(schema, root)
    if resolved is not schema:
        return schema_references(resolved, root)

    reference = schema.get("$ref")
    if isinstance(reference, str) and not reference.startswith("#/"):
        return (reference,)

    return tuple(
        reference
        for branch in schema.get("allOf", [])
        if isinstance(branch, Mapping)
        for reference in schema_references(branch, root)
    )
