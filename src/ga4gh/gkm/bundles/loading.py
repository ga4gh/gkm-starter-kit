"""Bundle loading entry points."""

from __future__ import annotations

import io
import json
from collections.abc import Mapping
from os import PathLike
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, TypeAlias

from .compatibility import check_gkm_version_compatibility
from .containers import Bundle, BundleCollection
from .errors import BundleConflictError, BundleNotFoundError, BundleSerializationError
from .model_conversion import parse_gks_values
from .pointers import validate_and_expand_bundle_references
from .registry import registry
from .schema_validation import prepare_bundle_schema, validate_bundle_schema

if TYPE_CHECKING:
    from .repository import BundleRepository

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
    :return: The value narrowed to a string-keyed dictionary.
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

    This loader handles local and in-memory sources. To load a published
    resource from the public repository, use :func:`load_repository_bundle`.

    Loading behavior:

    1. Decode the JSON document.
    2. Require and decode a producer JSON Schema. Verify the schema itself and
       check its GKM version compatibility before inspecting bundle content.
    3. Check the document and its metadata's basic shape.
    4. Walk the complete decoded document and validate bundle-local pointers
       before model conversion or bundle construction. Pointer failures are
       aggregated into one :class:`BundleReferenceError`; large error lists
       are truncated with total and omitted counts.
    5. Validate the complete document against the producer JSON Schema after
       pointer syntax and traversal have been checked.
    6. Convert recognized GKM objects to Pydantic models. Model validation is
       fail-fast; the first failure prevents a bundle from being returned.
       Producer-specific content remains dictionaries.

    :param source: Registered bundle name, file path, or readable JSON stream.
    :param schema: Producer JSON Schema using Draft 2020-12. A registered schema
        is used when omitted; one must be available from either source.
    :param serialization: Input serialization. Only ``"json"`` is supported.
        When omitted, JSON is assumed.
    :return: The loaded bundle.
    :raises ga4gh.gkm.bundles.BundleCompatibilityError: If the schema references
        unsupported GKM product versions.
    :raises BundleSerializationError: If the serialization or data shape is unsupported,
        or no producer JSON Schema is available.
    :raises ga4gh.gkm.bundles.BundleValidationError: If a recognized GKM object
        fails validation by its reference implementation.
    :raises ga4gh.gkm.bundles.BundleReferenceError: If one or more bundle-local
        JSON Pointers cannot be resolved.
    :raises BundleNotFoundError: If ``source`` cannot be found.
    """
    if serialization not in {None, "json"}:
        message = f"Unsupported serialization {serialization!r}; currently only 'json' is supported"
        raise BundleSerializationError(message)

    # 1. Decode the bundle document.
    raw_document, name, registered_schema = _read_json(source)

    # 2. Load, validate, and check compatibility of the producer schema.
    schema_source = schema if schema is not None else registered_schema
    if schema_source is None:
        message = "A bundle JSON Schema is required"
        raise BundleSerializationError(message)

    schema_document: Mapping[str, Any] | None = None
    schema_validator = None
    if schema_source is not None:
        raw_schema, _, _ = _read_json(schema_source)
        schema_document = _require_json_object(raw_schema, subject="schema")

        # Prepare once before inspecting bundle content. Pass the validator
        # below so instance validation does not repeat schema preparation.
        schema_validator = prepare_bundle_schema(schema_document)
        check_gkm_version_compatibility(schema_document)

    # 3. Check the decoded document's basic shape.
    document = _require_json_object(raw_document, subject="document")

    metadata = document.get("metadata", {})
    if not isinstance(metadata, Mapping):
        message = "Bundle metadata must be a JSON object"
        raise BundleSerializationError(message)

    # 4. Validate pointers and build the expanded document in one traversal.
    expanded_document = validate_and_expand_bundle_references(document)

    # 5. Validate the expanded document against the producer schema.
    validate_bundle_schema(
        expanded_document,
        schema_document,
        validator=schema_validator,
    )

    # 6. Convert recognized objects to reference-implementation models.
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
        schema=schema_document,
    )


def load_bundles(*sources: BundleSource) -> dict[str, Bundle]:
    """Load several local or in-memory bundles and key them by their names.

    For published repository resources, use :func:`load_repository_bundle`
    for each resource name.

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


def load_repository_bundle(
    repository: BundleRepository, name: str, *, refresh: bool = False
) -> Bundle:
    """Load and validate a bundle through a bundle repository.

    Loading behavior:

    1. Confirm ``name`` is indexed or completely saved locally.
    2. Retrieve the resource's ``bundle.json`` and ``bundle.schema.json``
       together. Saved local copies are reused by default; missing artifacts or
       ``refresh=True`` retrieve copies from the public repository.
    3. Pass both documents to :func:`load_bundle` for validation and conversion.
    4. Assign the repository resource name to the returned bundle.

    :param repository: Repository that resolves saved or public resource artifacts.
    :param name: Name of an indexed resource or complete locally saved resource.
    :param refresh: Whether to retrieve and replace the saved bundle and schema
        instead of reusing their local copies. A refresh requires the remote
        resource to remain available.
    :return: The validated bundle.
    :raises BundleRepositoryError: If the repository cannot provide either document.
    :raises BundleCompatibilityError: If the published schema is incompatible.
    :raises BundleSerializationError: If either document has an invalid shape.
    :raises BundleValidationError: If a recognized object fails validation.
    :raises BundleReferenceError: If a bundle-local reference is invalid.
    """
    bundle_data, schema_data = repository.get_bundle_documents(name, refresh=refresh)
    bundle = load_bundle(
        io.StringIO(json.dumps(bundle_data)),
        schema=io.StringIO(json.dumps(schema_data)),
    )
    bundle.name = name
    return bundle
