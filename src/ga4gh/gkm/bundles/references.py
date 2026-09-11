"""Adapters for models and bundle-local JSON Pointer references.

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

import inspect
from collections.abc import Mapping
from functools import cache
from typing import Any

from ga4gh.cat_vrs import models as cat_vrs_models
from ga4gh.core import models as core_models
from ga4gh.va_spec import aac_2017, acmg_2015, base, ccv_2022
from ga4gh.vrs import models as vrs_models
from pydantic import BaseModel, ValidationError

from .errors import (
    BundlePointerResolutionError,
    BundleReferenceError,
    BundleValidationError,
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


@cache
def _model_types() -> dict[str, type[BaseModel]]:
    """Discover concrete models exposed by GA4GH reference packages.

    :return: Model classes keyed by their GKS ``type`` value.
    """
    modules = [
        vrs_models,
        cat_vrs_models,
        core_models,
        base,
        aac_2017.models,
        acmg_2015.models,
        ccv_2022.models,
    ]

    types: dict[str, type[BaseModel]] = {}

    for module in modules:
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if not issubclass(candidate, BaseModel) or candidate is BaseModel:
                continue

            field = candidate.model_fields.get("type")
            if field is None or not isinstance(field.default, str):
                continue

            types.setdefault(field.default, candidate)

    return types


def _contains_bundle_reference(value: Any) -> bool:
    """Return whether a value contains a bundle-local JSON Pointer."""
    if isinstance(value, str):
        return value.startswith("#/")

    if isinstance(value, Mapping):
        return any(_contains_bundle_reference(item) for item in value.values())

    if isinstance(value, list):
        return any(_contains_bundle_reference(item) for item in value)
    return False


def _only_bundle_reference_errors(error: ValidationError) -> bool:
    """Return whether all errors are consequences of bundle-local references."""
    errors = error.errors()
    return bool(errors) and all(
        detail["type"] != "missing" and _contains_bundle_reference(detail.get("input"))
        for detail in errors
    )


def parse_gks_values(value: Any) -> Any:
    """Convert typed mappings with GA4GH reference implementations.

    The conversion is recursive. Recognized objects must be valid according to
    their installed reference implementation. Objects rejected only because a
    field contains a bundle-local JSON Pointer remain mappings.

    :param value: JSON-compatible value to inspect.
    :return: Reference models where possible, with other values preserved.
    """
    if isinstance(value, list):
        return [parse_gks_values(item) for item in value]

    if not isinstance(value, Mapping):
        return value

    type_name = value.get("type")
    model = _model_types().get(type_name) if isinstance(type_name, str) else None
    if model is not None:
        try:
            return model.model_validate(value)
        except ValidationError as error:
            if _only_bundle_reference_errors(error):
                return {key: parse_gks_values(item) for key, item in value.items()}

            message = f"Invalid {type_name!r} bundle object: {error}"
            raise BundleValidationError(message) from error

    return {key: parse_gks_values(item) for key, item in value.items()}
