"""Bundle-local JSON Pointer validation.

Bundle-local references use RFC 6901 JSON Pointer syntax:
``#/`` marks the bundle root, ``~0`` escapes ``~``, and ``~1`` escapes ``/``
within mapping keys.

For example:
* ``#/objects/item`` starts at the bundle root and selects ``item``.
* ``#/objects/a~1b`` selects the key ``a/b``.
* ``#/objects/a~0b`` selects the key ``a~b``.
"""

# ruff: noqa: ANN401

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .errors import (
    BundlePointerResolutionError,
    BundleReferenceError,
)

_MAX_BUNDLE_REFERENCE_ERRORS = 50


def _resolve_json_pointer(document: Any, pointer: str) -> Any:
    """Resolve an RFC 6901 JSON Pointer against a decoded JSON document.

    :param document: Decoded JSON document used as the pointer root.
    :param pointer: Bundle-local JSON Pointer beginning with ``#/``.
    :return: The value addressed by ``pointer``.
    :raises BundlePointerResolutionError: If traversal cannot be completed.
    """
    value = document
    for raw_part in pointer[2:].split("/"):
        # Every ``~`` must begin a valid ``~0`` or ``~1`` escape.
        if any(
            raw_part[index] == "~"
            and (index + 1 == len(raw_part) or raw_part[index + 1] not in "01")
            for index in range(len(raw_part))
        ):
            msg = (
                f"invalid JSON Pointer escape in path segment {raw_part!r}; "
                "'~' must be followed by '0' or '1'"
            )
            raise BundlePointerResolutionError(msg)

        part = raw_part.replace("~1", "/").replace("~0", "~")

        if isinstance(value, Mapping):
            # Object segments select a key in the current dictionary.
            try:
                value = value[part]
            except KeyError as error:
                msg = f"object member {part!r} does not exist"
                raise BundlePointerResolutionError(msg) from error
        elif isinstance(value, list):
            # Array segments must be a non-negative index with no leading zero.
            if part != "0" and (not part.isdigit() or part.startswith("0")):
                msg = (
                    f"invalid JSON Pointer array index {part!r}; expected '0' "
                    "or a non-zero digit followed by digits"
                )
                raise BundlePointerResolutionError(msg)

            index = int(part)

            # A valid index must still point to an existing array element.
            if index >= len(value):
                msg = f"array index {part!r} is out of bounds for length {len(value)}"
                raise BundlePointerResolutionError(msg)

            value = value[index]
        else:
            # JSON Pointer traversal cannot continue through a scalar value.
            msg = f"cannot traverse scalar value at path segment {part!r}"
            raise BundlePointerResolutionError(msg)
    return value


def validate_bundle_references(document: Mapping[str, Any]) -> None:
    """Validate all bundle-local JSON Pointers in a decoded bundle.

    The complete document is traversed even after failures are found. Only a
    bounded number of failure details are retained for the exception message.

    :param document: Decoded bundle document to inspect.
    :raises BundleReferenceError: If one or more local pointers cannot resolve.
    """
    failures: list[tuple[str, str, str]] = []
    failure_count = 0

    def validate_value(value: Any, path: str) -> None:
        """Recursively inspect one value for unresolved local pointers.

        :param value: Decoded JSON value to inspect.
        :param path: JSON path of ``value`` within the bundle document.
        """
        nonlocal failure_count
        if isinstance(value, str) and value.startswith("#/"):
            # Resolve against the original document so pointers can target any
            # collection, metadata, or producer-specific top-level value.
            try:
                _resolve_json_pointer(document, value)
            except BundlePointerResolutionError as error:
                failure_count += 1
                # Scan all values, but cap the number of reported details.
                if len(failures) < _MAX_BUNDLE_REFERENCE_ERRORS:
                    failures.append(
                        (value, path, str(error) or error.__class__.__name__)
                    )
            return

        # Recurse through objects and arrays while preserving each value's
        # location for error details.
        if isinstance(value, Mapping):
            for key, item in value.items():
                validate_value(item, f"{path}/{key}" if path else f"/{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                validate_value(item, f"{path}/{index}")

    # Begin validation at the document root.
    validate_value(document, "")
    if not failures:
        return

    # Format the collected failures as one bounded error message.
    details = "\n".join(
        f"- {pointer!r} at {path}: {reason}" for pointer, path, reason in failures
    )
    omitted = failure_count - len(failures)
    if omitted:
        details += f"\n- ... and {omitted} additional failure(s)"
    message = f"Invalid bundle references ({failure_count} total):\n{details}"
    raise BundleReferenceError(message)
