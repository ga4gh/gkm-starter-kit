"""Bun loading entry points."""

from __future__ import annotations

import json
from collections.abc import Mapping
from os import PathLike
from pathlib import Path
from typing import IO, Any, TypeAlias

from .catalog import catalog
from .compatibility import check_gkm_version_compatibility
from .errors import BunFormatError, BunNotFoundError
from .models import Bun, BunCollection
from .references import parse_gks_values

BunSource: TypeAlias = str | PathLike[str] | IO[str] | IO[bytes]


def _decode_json(source: IO[str] | IO[bytes]) -> object:
    """Decode a JSON stream and translate parser failures to bun errors.

    :param source: Readable text or binary JSON stream.
    :return: The decoded JSON value.
    :raises BunFormatError: If the stream does not contain valid JSON.
    """
    try:
        return json.load(source)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        name = getattr(source, "name", None)
        location = f" in {name!s}" if name is not None else ""
        message = f"Invalid JSON{location}: {error}"
        raise BunFormatError(message) from error


def _read_json(
    source: BunSource,
) -> tuple[object, str | None, Path | None]:
    """Read a JSON document and determine its bun name.

    :param source: Registered bun name, file path, or readable JSON stream.
    :return: Decoded JSON object, inferred name, and registered schema path.
    :raises BunNotFoundError: If ``source`` is neither a file nor a registered bun.
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
        registration = catalog.get_registration(source)
        if not registration.source.is_file():
            message = f"Bun source does not exist: {registration.source}"
            raise BunNotFoundError(message)

        with registration.source.open(encoding="utf-8") as stream:
            return _decode_json(stream), registration.name, registration.schema

    message = f"Bun source does not exist: {path}"
    raise BunNotFoundError(message)


def _require_json_object(value: object, *, subject: str) -> Mapping[str, Any]:
    """Return a decoded JSON object or raise a bun format error.

    :param value: Decoded JSON value.
    :param subject: Human-readable name used in an error message.
    :return: The value narrowed to a string-keyed mapping.
    :raises BunFormatError: If ``value`` is not a JSON object.
    """
    if isinstance(value, Mapping):
        return value

    message = f"A bun {subject} must be a JSON object"
    raise BunFormatError(message)


def load_bun(
    source: BunSource,
    *,
    schema: BunSource | None = None,
    serialization: str | None = None,
) -> Bun:
    """Load one bun from a registered name, JSON file, or JSON stream.

    Objects accepted by a GA4GH reference implementation are returned as its
    Pydantic models. Producer-specific structures and objects containing bundle
    references that cannot be validated independently remain mappings.

    :param source: Registered bun name, file path, or readable JSON stream.
    :param schema: Producer JSON Schema. A registered schema is used when omitted.
    :param serialization: Input serialization. Only ``"json"`` is supported.
        When omitted, JSON is assumed.
    :return: The loaded bun.
    :raises gkm.starter.buns.BunCompatibilityError: If the schema references
        unsupported GKM product versions.
    :raises BunFormatError: If the serialization or document shape is unsupported.
    :raises BunNotFoundError: If ``source`` cannot be found.
    """
    if serialization not in {None, "json"}:
        message = f"Unsupported serialization {serialization!r}; currently only 'json' is supported"
        raise BunFormatError(message)

    raw_document, name, registered_schema = _read_json(source)

    schema_source = schema if schema is not None else registered_schema
    if schema_source is not None:
        raw_schema, _, _ = _read_json(schema_source)
        schema_document = _require_json_object(raw_schema, subject="schema")

        check_gkm_version_compatibility(schema_document)

    document = _require_json_object(raw_document, subject="document")

    metadata = document.get("metadata", {})
    collections: dict[str, BunCollection] = {}
    extras: dict[str, Any] = {}
    for collection_name, values in document.items():
        if collection_name == "metadata" or not isinstance(values, Mapping):
            if collection_name != "metadata":
                extras[collection_name] = values
            continue

        parsed = parse_gks_values(values)
        collections[collection_name] = BunCollection(collection_name, parsed)

    return Bun(
        collections,
        metadata=metadata if isinstance(metadata, Mapping) else {},
        extras=extras,
        name=name,
    )


def load_buns(*sources: BunSource) -> dict[str, Bun]:
    """Load several buns and key them by their resolved names.

    :param sources: Registered bun names, file paths, or readable JSON streams.
    :return: Loaded buns keyed by name.
    :raises ValueError: If two sources resolve to the same name.
    """
    loaded: dict[str, Bun] = {}

    for source in sources:
        bun = load_bun(source)
        key = bun.name or f"bun-{len(loaded) + 1}"

        if key in loaded:
            message = f"Multiple buns resolved to the name {key!r}"
            raise ValueError(message)

        loaded[key] = bun

    return loaded
