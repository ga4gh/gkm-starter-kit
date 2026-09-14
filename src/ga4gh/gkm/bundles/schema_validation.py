"""Draft 2020-12 JSON Schema validation for serialized bundles."""

from __future__ import annotations

import json
from collections.abc import Mapping  # noqa: TC003
from functools import cache
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT202012

from .errors import BundleSerializationError, BundleValidationError
from .model_conversion import _model_types

_DRAFT_202012_META_SCHEMA = "https://json-schema.org/draft/2020-12/schema"


def _require_draft_202012(schema: Mapping[str, Any]) -> None:
    """Require a producer schema to declare JSON Schema Draft 2020-12.

    :param schema: Producer JSON Schema to check.
    :raises BundleSerializationError: If the schema does not declare Draft
        2020-12.
    """
    if schema.get("$schema") != _DRAFT_202012_META_SCHEMA:
        message = (
            "Bundle JSON Schema must declare Draft 2020-12 with "
            f"'$schema': {_DRAFT_202012_META_SCHEMA!r}"
        )
        raise BundleSerializationError(message)


@cache
def _reference_store() -> dict[str, Mapping[str, Any]]:
    """Build a local store of schemas exposed by installed GA4GH models."""
    store: dict[str, Mapping[str, Any]] = {}
    for model in _model_types().values():
        try:
            schema = model.model_json_schema()
        except (AttributeError, TypeError, ValueError):
            continue

        identifier = schema.get("$id")
        if isinstance(identifier, str):
            local_schema = dict(schema)
            local_schema.pop("$id", None)
            store[identifier] = local_schema
    return store


@cache
def _reference_registry() -> Registry:
    """Build a registry of schemas exposed by installed GA4GH models."""
    return Registry().with_resources(
        (
            identifier,
            Resource.from_contents(schema, default_specification=DRAFT202012),
        )
        for identifier, schema in _reference_store().items()
    )


@cache
def _compiled_validator(schema_json: str) -> Draft202012Validator:
    """Return a compiled validator for a canonical schema document.

    :param schema_json: Canonically serialized JSON Schema document.
    :returns: A cached Draft 2020-12 validator.
    :raises SchemaError: If the schema is invalid.
    """
    schema = json.loads(schema_json)
    validator = Draft202012Validator(
        schema,
        registry=_reference_registry(),
    )
    validator.check_schema(schema)
    return validator


def prepare_bundle_schema(schema: Mapping[str, Any]) -> Draft202012Validator:
    """Compile and check a producer schema before bundle processing.

    :param schema: Producer JSON Schema to prepare.
    :returns: The cached validator for ``schema``.
    :raises BundleSerializationError: If the schema is invalid or cannot be
        prepared for validation, including when it does not declare Draft 2020-12.
    """
    try:
        _require_draft_202012(schema)
        schema_json = json.dumps(
            schema,
            sort_keys=True,
            separators=(",", ":"),
        )
        return _compiled_validator(schema_json)
    except BundleSerializationError:
        raise
    except (SchemaError, TypeError, ValueError) as error:
        message = f"Invalid bundle JSON Schema: {error}"
        raise BundleSerializationError(message) from error


def validate_bundle_schema(
    document: Mapping[str, Any],
    schema: Mapping[str, Any],
    *,
    validator: Draft202012Validator | None = None,
) -> None:
    """Validate a bundle document against its producer JSON Schema.

    Bundle-local JSON Pointers are expanded before validation so schemas can
    describe the referenced objects rather than their serialized pointers.

    :param document: Decoded bundle document to validate.
    :param schema: Producer JSON Schema used for validation.
    :param validator: Prepared validator for ``schema``, when already available.
    :raises BundleSerializationError: If the schema is invalid or a reference
        cannot be resolved locally.
    :raises BundleValidationError: If the document violates the schema.
    """
    try:
        # Standalone callers may not provide a prepared validator.
        prepared_validator = (
            validator if validator is not None else prepare_bundle_schema(schema)
        )
        error = next(prepared_validator.iter_errors(document), None)
    except (SchemaError, Unresolvable) as error:
        message = f"Bundle JSON Schema reference could not be resolved locally: {error}"
        raise BundleSerializationError(message) from error

    if error is not None:
        path = "/".join(str(part) for part in error.absolute_path) or "/"
        message = f"Bundle does not match its JSON Schema at {path}: {error.message}"
        raise BundleValidationError(message) from error
