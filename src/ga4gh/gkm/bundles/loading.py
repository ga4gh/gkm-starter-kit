"""Bundle loading entry points."""

from __future__ import annotations

import json
from collections.abc import Mapping
from os import PathLike
from pathlib import Path
from typing import IO, Any, TypeAlias

from .compatibility import check_gkm_version_compatibility
from .errors import BundleConflictError, BundleNotFoundError, BundleSerializationError
from .models import Bundle, BundleCollection
from .references import parse_gks_values
from .registry import registry

BundleSource: TypeAlias = str | PathLike[str] | IO[str] | IO[bytes]


def _decode_json(source: IO[str] | IO[bytes]) -> object:
    """Decode a JSON stream and translate parser failures to bundle errors.

    :param source: Readable text or binary JSON stream.
    :return: The decoded JSON value.
    :raises BundleSerializationError: If the stream does not contain valid JSON.
    """
    try:
        return json.load(source)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        name = getattr(source, "name", None)
        location = f" in {name!s}" if name is not None else ""
        message = f"Invalid JSON{location}: {error}"
        raise BundleSerializationError(message) from error


def _read_json(
    source: BundleSource,
) -> tuple[object, str | None, Path | None]:
    """Read a JSON document and determine its bundle name.

    :param source: Registered bundle name, file path, or readable JSON stream.
    :return: Decoded JSON object, inferred name, and registered schema path.
    :raises BundleNotFoundError: If ``source`` is neither a file nor a registered bundle.
    """
    if hasattr(source, "read"):
        value = _decode_json(source)
        stream_name = getattr(source, "name", None)
        name = (
            Path(stream_name).stem if isinstance(stream_name, (str, PathLike)) else None
        )
        return value, name, None

    path = Path(source)
    if path.is_file():
        with path.open(encoding="utf-8") as stream:
            return _decode_json(stream), path.stem, None

    if isinstance(source, str):
        registration = registry.get_registration(source)
        if not registration.source.is_file():
            message = f"Bundle source does not exist: {registration.source}"
            raise BundleNotFoundError(message)

        with registration.source.open(encoding="utf-8") as stream:
            return _decode_json(stream), registration.name, registration.schema

    message = f"Bundle source does not exist: {path}"
    raise BundleNotFoundError(message)


def _require_json_object(value: object, *, subject: str) -> Mapping[str, Any]:
    """Return a decoded JSON object or raise a bundle serialization error.

    :param value: Decoded JSON value.
    :param subject: Human-readable name used in an error message.
    :return: The value narrowed to a string-keyed mapping.
    :raises BundleSerializationError: If ``value`` is not a JSON object.
    """
    if isinstance(value, Mapping):
        return value

    message = f"A bundle {subject} must be a JSON object"
    raise BundleSerializationError(message)


def load_bundle(
    source: BundleSource,
    *,
    schema: BundleSource | None = None,
    serialization: str | None = None,
) -> Bundle:
    """Load one bundle from a registered name, JSON file, or JSON stream.

    Objects recognized by a GA4GH reference implementation are validated and
    returned as its Pydantic models. Producer-specific structures and objects
    containing bundle-local references that cannot be validated independently
    remain mappings.

    Loading is fail-fast. If any recognized GKM object fails reference-model
    validation, no bundle is returned.

    When a schema is provided, it is used to check GKM version compatibility.
    The bundle is not fully validated against the schema.

    :param source: Registered bundle name, file path, or readable JSON stream.
    :param schema: Producer JSON Schema. A registered schema is used when omitted.
    :param serialization: Input serialization. Only ``"json"`` is supported.
        When omitted, JSON is assumed.
    :return: The loaded bundle.
    :raises ga4gh.gkm.bundles.BundleCompatibilityError: If the schema references
        unsupported GKM product versions.
    :raises BundleSerializationError: If the serialization or data shape is unsupported.
    :raises ga4gh.gkm.bundles.BundleValidationError: If a recognized GKM object
        fails validation by its reference implementation.
    :raises BundleNotFoundError: If ``source`` cannot be found.
    """
    if serialization not in {None, "json"}:
        message = f"Unsupported serialization {serialization!r}; currently only 'json' is supported"
        raise BundleSerializationError(message)

    raw_document, name, registered_schema = _read_json(source)

    schema_source = schema if schema is not None else registered_schema
    if schema_source is not None:
        raw_schema, _, _ = _read_json(schema_source)
        schema_document = _require_json_object(raw_schema, subject="schema")

        check_gkm_version_compatibility(schema_document)

    document = _require_json_object(raw_document, subject="document")

    metadata = document.get("metadata", {})
    if not isinstance(metadata, Mapping):
        message = "Bundle metadata must be a JSON object"
        raise BundleSerializationError(message)

    collections: dict[str, BundleCollection] = {}
    extras: dict[str, Any] = {}
    for collection_name, values in document.items():
        if collection_name == "metadata" or not isinstance(values, Mapping):
            if collection_name != "metadata":
                extras[collection_name] = values
            continue

        parsed = parse_gks_values(values)
        collections[collection_name] = BundleCollection(collection_name, parsed)

    return Bundle(
        collections,
        metadata=metadata,
        extras=extras,
        name=name,
    )


def load_bundles(*sources: BundleSource) -> dict[str, Bundle]:
    """Load several bundles and key them by their resolved names.

    :param sources: Registered bundle names, file paths, or readable JSON streams.
    :return: Loaded bundles keyed by name.
    :raises BundleConflictError: If two sources resolve to the same name.
    """
    loaded: dict[str, Bundle] = {}

    for source in sources:
        bundle = load_bundle(source)
        key = bundle.name or f"bundle-{len(loaded) + 1}"

        if key in loaded:
            message = f"Multiple bundles resolved to the name {key!r}"
            raise BundleConflictError(message)

        loaded[key] = bundle

    return loaded
