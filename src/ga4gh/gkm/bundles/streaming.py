"""Streaming, whole-bundle validation with a stamped verification report.

:func:`validate_bundle_stream` validates every record of a serialized bundle
without loading the whole document into memory, so multi-gigabyte published
bundles (optionally gzip-compressed) can be checked exactly as distributed.

The bundle is parsed incrementally with `ijson <https://pypi.org/project/ijson/>`_,
an optional dependency installed with the ``streaming`` extra. Every record is
validated **verbatim**: records are grouped into chunks of one section, each
chunk is wrapped as a one-section bundle document, and the chunk is validated
against the producer JSON Schema with
:func:`~ga4gh.gkm.bundles.schema_validation.validate_bundle_schema`. A failing
chunk is re-validated record by record to identify the failing records.

Top-level values that are not sections (scalars, arrays, and ``metadata``) are
validated together once the whole document has been read. The schema's
top-level ``required`` list is checked against the top-level keys present in
the document rather than against each one-section chunk.

Limitations of streaming validation:

* Bundle-local JSON Pointers (``#/...``) are neither resolved nor expanded,
  because their targets may lie anywhere in the document. Records containing
  them are counted and reported in a warning.
* Constraints that depend on a whole section at once, such as a section's
  ``maxProperties``, are evaluated per chunk.
"""

# ruff: noqa: ANN401

from __future__ import annotations

import collections
import contextlib
import datetime
import gzip
import hashlib
import json
import logging
import os
import platform
import re
from collections.abc import Iterable, Iterator, Mapping
from concurrent.futures import Future, ProcessPoolExecutor
from dataclasses import dataclass, field
from importlib import metadata
from os import PathLike
from pathlib import Path
from typing import IO, Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from .compatibility import check_gkm_version_compatibility
from .errors import (
    BundleCompatibilityError,
    BundleError,
    BundleNotFoundError,
    BundleSerializationError,
)
from .model_conversion import _contains_bundle_reference
from .registry import registry as bundle_registry
from .schema_resolution import (
    _resolve_local_reference,
    schema_for_pointer,
    schema_references,
)
from .schema_validation import (
    _reference_store,
    _require_draft_202012,
    validate_bundle_schema,
)

_logger = logging.getLogger(__name__)

REPORT_VERSION = 1
"""Version of the report document layout written by :meth:`StreamValidationResult.to_dict`."""

_MAX_FAILURE_SAMPLES = 50
_MAX_MESSAGE_LENGTH = 500
_GZIP_MAGIC = b"\x1f\x8b"
_SCHEMA_FILE_SUFFIXES = {"", ".json"}
_COMBINING_KEYWORDS = ("oneOf", "anyOf", "allOf")
# GKM schema URLs follow ``.../<standard>/<version>/json/<Name>``.
_GKM_SCHEMA_URL = re.compile(
    r"/(?P<standard>[^/]+)/(?P<version>[^/]+)/json/[^/#]+$",
)
_REPORTED_DISTRIBUTIONS = (
    "ga4gh.gkm",
    "ga4gh.vrs",
    "ga4gh.cat_vrs",
    "ga4gh.va_spec",
    "jsonschema",
    "referencing",
    "ijson",
)
_NO_COUNT = "\N{EN DASH}"
_START_EVENTS = ("start_map", "start_array")
_END_EVENTS = ("end_map", "end_array")


@dataclass(frozen=True, slots=True)
class SchemaFile:
    """A JSON Schema document read from a local file.

    :param identifier: The schema's ``$id``.
    :param path: File the schema was read from.
    :param sha256: SHA-256 digest of the file's bytes.
    :param contents: Decoded schema document.
    """

    identifier: str
    path: Path
    sha256: str
    contents: Mapping[str, Any] = field(repr=False)


def load_schema_directory(
    *directories: str | PathLike[str],
) -> dict[str, SchemaFile]:
    """Collect JSON Schemas with an ``$id`` from local directories.

    Directories are searched recursively, following symbolic links. Files named
    ``*.json`` or without a suffix (the layout GKM schema repositories use for
    their ``json/`` folders) are read; files that are not JSON objects with a
    string ``$id`` are ignored.

    :param directories: Directories to search.
    :return: Schema files keyed by ``$id``.
    :raises BundleNotFoundError: If a directory does not exist.
    :raises BundleSerializationError: If two files declare the same ``$id``
        with different contents.
    """
    found: dict[str, SchemaFile] = {}
    for directory in directories:
        root = Path(directory)
        if not root.is_dir():
            message = f"Schema directory does not exist: {root}"
            raise BundleNotFoundError(message)

        for path in _schema_candidate_files(root):
            schema_file = _read_schema_file(path)
            if schema_file is None:
                continue

            existing = found.get(schema_file.identifier)
            if existing is None:
                found[schema_file.identifier] = schema_file
            elif existing.contents != schema_file.contents:
                message = (
                    f"Schema $id {schema_file.identifier!r} is declared with "
                    f"different contents in {existing.path} and {schema_file.path}"
                )
                raise BundleSerializationError(message)
    return found


def _schema_candidate_files(root: Path) -> Iterator[Path]:
    """Yield candidate schema files below ``root`` in a stable order.

    :param root: Directory to search.
    :return: Files whose suffix may hold a JSON Schema.
    """
    visited: set[str] = set()
    for directory, directory_names, file_names in os.walk(root, followlinks=True):
        real = os.path.realpath(directory)
        if real in visited:
            # Guard against symbolic-link cycles.
            directory_names[:] = []
            continue
        visited.add(real)
        directory_names.sort()
        for name in sorted(file_names):
            path = Path(directory) / name
            if path.suffix in _SCHEMA_FILE_SUFFIXES and not name.startswith("."):
                yield path


def _read_schema_file(path: Path) -> SchemaFile | None:
    """Read a schema file, or return ``None`` when it is not an identified schema.

    :param path: Candidate file.
    :return: The schema file, or ``None``.
    """
    try:
        raw = path.read_bytes()
        contents = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    if not isinstance(contents, dict) or not isinstance(contents.get("$id"), str):
        return None

    return SchemaFile(
        identifier=contents["$id"],
        path=path,
        sha256=hashlib.sha256(raw).hexdigest(),
        contents=contents,
    )


def build_schema_registry(
    schema_files: Mapping[str, SchemaFile] | None = None,
) -> Registry:
    """Build a ``referencing`` registry for validating bundle records.

    The registry holds the schemas exposed by the installed GA4GH reference
    implementations, which :func:`~ga4gh.gkm.bundles.schema_validation.validate_bundle_schema`
    uses by default, plus the given local schema files. A local file takes
    precedence over an installed model schema with the same ``$id``, so a
    producer can validate against exactly the schemas it publishes.

    :param schema_files: Local schemas keyed by ``$id``, as returned by
        :func:`load_schema_directory`.
    :return: The combined registry.
    """
    return _registry_from_store(_combined_store(schema_files or {}))


def _combined_store(
    schema_files: Mapping[str, SchemaFile],
) -> dict[str, Mapping[str, Any]]:
    """Combine installed model schemas with local schema files.

    :param schema_files: Local schemas keyed by ``$id``.
    :return: Schema contents keyed by ``$id``; local files win.
    """
    store = dict(_reference_store())
    store.update(
        {identifier: file.contents for identifier, file in schema_files.items()}
    )
    return store


def _registry_from_store(store: Mapping[str, Mapping[str, Any]]) -> Registry:
    """Build a registry from schema contents keyed by ``$id``.

    :param store: Schema contents keyed by ``$id``.
    :return: The registry.
    """
    return Registry().with_resources(
        (
            identifier,
            Resource.from_contents(contents, default_specification=DRAFT202012),
        )
        for identifier, contents in store.items()
    )


def _record_validator(
    schema: Mapping[str, Any], registry: Registry
) -> Draft202012Validator:
    """Compile the validator applied to one-section chunk documents.

    :param schema: Producer bundle JSON Schema.
    :param registry: Registry used to resolve external references.
    :return: A validator for the schema without its top-level ``required`` list.
    :raises BundleSerializationError: If the schema is invalid.
    """
    try:
        _require_draft_202012(schema)
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        message = f"Invalid bundle JSON Schema: {error}"
        raise BundleSerializationError(message) from error

    # A chunk holds one section; the top-level ``required`` list is checked
    # once against the keys of the whole document instead.
    chunk_schema = {key: value for key, value in schema.items() if key != "required"}
    return Draft202012Validator(chunk_schema, registry=registry)


class _ChunkValidator:
    """Validate chunks of records from one section."""

    def __init__(
        self, schema: Mapping[str, Any], store: Mapping[str, Mapping[str, Any]]
    ) -> None:
        """Compile the chunk validator.

        :param schema: Producer bundle JSON Schema.
        :param store: Schema contents keyed by ``$id``.
        """
        self.schema = schema
        self.validator = _record_validator(schema, _registry_from_store(store))

    def first_error(self, document: Mapping[str, Any]) -> str | None:
        """Return a validation error message, or ``None`` when valid.

        :param document: Document to validate.
        :return: The error message, if any.
        """
        try:
            validate_bundle_schema(document, self.schema, validator=self.validator)
        except BundleError as error:
            return str(error)[:_MAX_MESSAGE_LENGTH]
        return None

    def __call__(
        self, section: str, items: list[tuple[str, Any]]
    ) -> tuple[str, int, list[tuple[str, str]], int]:
        """Validate one chunk of records.

        :param section: Section name.
        :param items: ``(key, record)`` pairs.
        :return: Section name, record count, ``(key, message)`` failures, and
            the number of records that contain bundle-local pointers.
        """
        with_pointers = sum(
            1 for _, record in items if _contains_bundle_reference(record)
        )
        if self.first_error({section: dict(items)}) is None:
            return section, len(items), [], with_pointers

        failures = []
        for key, record in items:
            message = self.first_error({section: {key: record}})
            if message is not None:
                failures.append((key, message))
        if not failures:
            failures.append(("", "chunk failed but no single record reproduces it"))
        return section, len(items), failures, with_pointers


_WORKER_VALIDATOR: _ChunkValidator | None = None


def _init_worker(
    schema: Mapping[str, Any], store: Mapping[str, Mapping[str, Any]]
) -> None:
    """Compile the chunk validator once per worker process.

    :param schema: Producer bundle JSON Schema.
    :param store: Schema contents keyed by ``$id``.
    """
    global _WORKER_VALIDATOR  # noqa: PLW0603
    _WORKER_VALIDATOR = _ChunkValidator(schema, store)


def _validate_in_worker(
    section: str, items: list[tuple[str, Any]]
) -> tuple[str, int, list[tuple[str, str]], int]:
    """Validate a chunk with the worker's validator.

    :param section: Section name.
    :param items: ``(key, record)`` pairs.
    :return: See :meth:`_ChunkValidator.__call__`.
    """
    if _WORKER_VALIDATOR is None:  # pragma: no cover - set by the initializer
        message = "Worker validator is not initialized"
        raise RuntimeError(message)
    return _WORKER_VALIDATOR(section, items)


class _HashingReader:
    """Readable binary stream that hashes and counts every byte read."""

    def __init__(self, stream: IO[bytes]) -> None:
        """Wrap a binary stream.

        :param stream: Stream to read from.
        """
        self.stream = stream
        self.digest = hashlib.sha256()
        self.size = 0

    def read(self, size: int = -1) -> bytes:
        """Read and hash bytes.

        :param size: Maximum number of bytes, or ``-1`` for all.
        :return: The bytes read.
        """
        data = self.stream.read(size)
        self.digest.update(data)
        self.size += len(data)
        return data

    def drain(self) -> None:
        """Read and hash any bytes the parser did not consume."""
        while self.read(1 << 20):
            pass


_HEADER = "header"
_SECTION = "section"
_RECORD = "record"


def iter_bundle_items(stream: IO[bytes]) -> Iterator[tuple[str, str, str | None, Any]]:
    """Stream the top-level values, sections, and records of a bundle document.

    Yields ``(kind, name, key, value)`` tuples, where ``kind`` is:

    * ``"header"`` for a top-level value that is not a section (a scalar, an
      array, or ``metadata``); ``key`` is ``None``.
    * ``"section"`` when a section (any other top-level object) begins; ``key``
      and ``value`` are ``None``.
    * ``"record"`` for each entry of a section, with its key and value.

    Nesting depth is tracked from the parser's start and end events, never from
    the ``ijson`` prefix: record keys such as ``ga4gh:SL.x`` or
    ``clinvar.submission:SCV1.2`` contain dots, which the prefix also uses as
    its separator.

    :param stream: Uncompressed binary JSON stream.
    :return: An iterator over the document's items.
    :raises BundleSerializationError: If the document is not a JSON object or
        is not valid JSON.
    :raises ImportError: If ``ijson`` is not installed.
    """
    try:
        import ijson  # noqa: PLC0415
    except ImportError as error:  # pragma: no cover - depends on the environment
        message = (
            "Streaming bundle validation requires ijson; install it with "
            "'pip install \"ga4gh.gkm[streaming]\"'"
        )
        raise ImportError(message) from error

    depth = 0
    top_key: str | None = None
    record_key: str | None = None
    builder: Any = None
    builder_depth = 0
    target: tuple[str, str, str | None] = (_HEADER, "", None)

    try:
        for _, event, value in ijson.parse(stream, use_float=True):
            if builder is not None:
                builder.event(event, value)
                if event in _START_EVENTS:
                    builder_depth += 1
                elif event in _END_EVENTS:
                    builder_depth -= 1
                    if builder_depth == 0:
                        yield (*target, builder.value)
                        builder = None
                continue

            if depth == 0:
                if event != "start_map":
                    message = "A bundle document must be a JSON object"
                    raise BundleSerializationError(message)
                depth = 1
            elif depth == 1:
                if event == "map_key":
                    top_key = value
                elif event == "start_map" and top_key != "metadata":
                    depth = 2
                    yield _SECTION, str(top_key), None, None
                elif event in _START_EVENTS:
                    builder, builder_depth = ijson.ObjectBuilder(), 1
                    builder.event(event, value)
                    target = (_HEADER, str(top_key), None)
                elif event == "end_map":
                    depth = 0
                else:
                    yield _HEADER, str(top_key), None, value
            elif event == "map_key":
                record_key = value
            elif event in _START_EVENTS:
                builder, builder_depth = ijson.ObjectBuilder(), 1
                builder.event(event, value)
                target = (_RECORD, str(top_key), record_key)
            elif event == "end_map":
                depth = 1
            else:
                yield _RECORD, str(top_key), record_key, value
    except ijson.JSONError as error:
        message = f"Invalid JSON in bundle: {error}"
        raise BundleSerializationError(message) from error


@dataclass
class StreamValidationResult:
    """Outcome and stamped verification report of :func:`validate_bundle_stream`.

    :param passed: Whether every check passed.
    :param report: The verification report as a JSON-compatible dictionary.
    """

    passed: bool
    report: dict[str, Any]

    @property
    def records(self) -> int:
        """Return the number of records read.

        :return: Records read across all sections.
        """
        return self.report["totals"]["records"]

    @property
    def failing(self) -> int:
        """Return the number of failing records and top-level values.

        :return: The failure count.
        """
        return self.report["totals"]["failing"]

    def to_dict(self) -> dict[str, Any]:
        """Return the verification report.

        :return: The report as a JSON-compatible dictionary.
        """
        return self.report

    def to_markdown(self) -> str:
        """Render the verification report as a Markdown summary.

        :return: The Markdown document.
        """
        return render_report_markdown(self.report)

    def write_report(self, path: str | PathLike[str]) -> tuple[Path, Path]:
        """Write the report as JSON and a Markdown summary beside it.

        :param path: JSON report destination. The Markdown summary is written
            to the same path with a ``.md`` suffix.
        :return: Paths of the JSON report and the Markdown summary.
        """
        json_path = Path(path)
        markdown_path = json_path.with_suffix(".md")
        json_path.write_text(json.dumps(self.report, indent=2) + "\n", encoding="utf-8")
        markdown_path.write_text(self.to_markdown(), encoding="utf-8")
        return json_path, markdown_path


@dataclass
class _Tally:
    """Counters accumulated while streaming a bundle."""

    order: list[str] = field(default_factory=list)
    headers: dict[str, Any] = field(default_factory=dict)
    records: collections.Counter[str] = field(default_factory=collections.Counter)
    failing: collections.Counter[str] = field(default_factory=collections.Counter)
    skipped: collections.Counter[str] = field(default_factory=collections.Counter)
    types: dict[str, collections.Counter[str]] = field(
        default_factory=lambda: collections.defaultdict(collections.Counter)
    )
    failures: list[str] = field(default_factory=list)
    with_pointers: int = 0

    def add(
        self, section: str, count: int, failures: list[tuple[str, str]], pointers: int
    ) -> None:
        """Record the outcome of one validated chunk.

        :param section: Section name.
        :param count: Records in the chunk.
        :param failures: ``(key, message)`` failures.
        :param pointers: Records that contain bundle-local pointers.
        """
        self.records[section] += count
        self.failing[section] += len(failures)
        self.with_pointers += pointers
        for key, message in failures:
            self.add_failure(f"{section}/{key}: {message}")

    def add_failure(self, failure: str) -> None:
        """Keep a bounded sample of failure messages.

        :param failure: Failure description.
        """
        if len(self.failures) < _MAX_FAILURE_SAMPLES:
            self.failures.append(failure)


def validate_bundle_stream(
    source: str | PathLike[str],
    schema: str | PathLike[str] | Mapping[str, Any] | None = None,
    *,
    schema_id: str | None = None,
    schema_dirs: Iterable[str | PathLike[str]] = (),
    workers: int = 1,
    chunk_size: int = 2000,
    sidecar: str | PathLike[str] | None = None,
    url: str | None = None,
    sections: Iterable[str] | None = None,
    allow_empty_sections: bool = False,
) -> StreamValidationResult:
    """Validate every record of a bundle file and build a verification report.

    The bundle is read once as a stream, so it never has to fit in memory. A
    gzip-compressed file is detected from its content and decompressed while
    reading. The SHA-256 digest of the bytes actually read is recorded and, when
    a ``.sha256`` sidecar is available, compared with it.

    The bundle passes when:

    * every top-level property with a ``const`` in the schema has that value;
    * every top-level property the schema requires is present;
    * the file's SHA-256 digest matches the sidecar, when one is available;
    * every section has at least one record, unless ``allow_empty_sections``;
    * every record and every other top-level value validates against the
      schema; and
    * every section was validated (``sections`` did not skip any).

    :param source: Path of the bundle file (``.json`` or gzip-compressed), or
        the name of a bundle registered in :data:`ga4gh.gkm.bundles.registry`.
    :param schema: Producer bundle JSON Schema, as a path or a decoded
        document. When omitted, the schema is found by ``schema_id`` or from the
        bundle's registration.
    :param schema_id: ``$id`` of the bundle schema, looked up in
        ``schema_dirs``. When ``schema`` is also given, its ``$id`` must match.
    :param schema_dirs: Directories of JSON Schemas used to resolve the bundle
        schema's external references, in addition to the schemas of the
        installed GA4GH reference implementations. See
        :func:`load_schema_directory` and :func:`build_schema_registry`.
    :param workers: Number of processes validating chunks. ``1`` validates in
        the calling process.
    :param chunk_size: Maximum number of records per validated chunk.
    :param sidecar: Path of a file whose first token is the bundle's published
        SHA-256 digest. Defaults to ``<source>.sha256`` when that file exists.
    :param url: Published location of the bundle, recorded in the report.
    :param sections: Validate only these sections. Records of other sections
        are counted, not validated, and the report fails its skipped-section
        check.
    :param allow_empty_sections: Do not fail the report for empty sections.
        Empty sections are always validated against the schema.
    :return: Whether the bundle passed, and the verification report.
    :raises BundleNotFoundError: If the bundle, schema, or a schema directory
        cannot be found.
    :raises BundleSerializationError: If the schema is missing or invalid, or
        the bundle is not a JSON object.
    """
    if workers < 1 or chunk_size < 1:
        message = "workers and chunk_size must be positive"
        raise ValueError(message)

    started = datetime.datetime.now(datetime.UTC)
    bundle_path, registered_schema = _bundle_path(source)
    schema_dirs = [str(directory) for directory in schema_dirs]
    schema_files = load_schema_directory(*schema_dirs)
    schema_document, schema_file = _bundle_schema(
        schema if schema is not None else registered_schema, schema_id, schema_files
    )
    store = _combined_store(schema_files)
    validate_chunk = _ChunkValidator(schema_document, store)

    warnings = _compatibility_warnings(schema_document)
    only = set(sections) if sections is not None else None
    tally = _Tally()
    compressed = _is_gzip(bundle_path)
    hashing = _HashingReader(bundle_path.open("rb"))
    executor = (
        ProcessPoolExecutor(
            workers, initializer=_init_worker, initargs=(schema_document, store)
        )
        if workers > 1
        else None
    )
    pending: collections.deque[Future[Any]] = collections.deque()

    def submit(section: str, items: list[tuple[str, Any]]) -> None:
        if executor is None:
            tally.add(*validate_chunk(section, items))
            return
        pending.append(executor.submit(_validate_in_worker, section, items))
        # Bound in-flight work so the bundle is never buffered in memory.
        while len(pending) > workers * 3:
            tally.add(*pending.popleft().result())

    try:
        with (
            gzip.open(hashing, "rb") if compressed else contextlib.nullcontext(hashing)
        ) as stream:
            buffer: list[tuple[str, Any]] = []
            current: str | None = None
            for kind, name, key, value in iter_bundle_items(stream):
                if kind == _HEADER:
                    tally.headers[name] = value
                    continue
                if kind == _SECTION:
                    if buffer and current is not None:
                        submit(current, buffer)
                    buffer, current = [], name
                    tally.order.append(name)
                    tally.records[name] += 0
                    _logger.info("Streaming section %s", name)
                    continue
                if only is not None and name not in only:
                    tally.skipped[name] += 1
                    continue
                tally.types[name][_record_type(value)] += 1
                buffer.append((str(key), value))
                if len(buffer) >= chunk_size:
                    submit(name, buffer)
                    buffer = []
            if buffer and current is not None:
                submit(current, buffer)
        hashing.drain()
        while pending:
            tally.add(*pending.popleft().result())
    except (OSError, EOFError) as error:
        message = f"Unable to read bundle {bundle_path}: {error}"
        raise BundleSerializationError(message) from error
    finally:
        hashing.stream.close()
        if executor is not None:
            executor.shutdown(cancel_futures=True)

    # Validate top-level values and the shape of empty sections.
    header_failures = 0
    empty = [
        name
        for name in tally.order
        if tally.records[name] == 0 and name not in tally.skipped
    ]
    header_document = dict(tally.headers) | {name: {} for name in empty}
    header_error = validate_chunk.first_error(header_document)
    if header_error is not None:
        header_failures = 1
        tally.add_failure(f"(top level): {header_error}")

    finished = datetime.datetime.now(datetime.UTC)
    report = _build_report(
        started=started,
        finished=finished,
        bundle_path=bundle_path,
        url=url,
        compressed=compressed,
        hashing=hashing,
        sidecar=_sidecar_digest(bundle_path, sidecar),
        schema_document=schema_document,
        schema_file=schema_file,
        schema_files=schema_files,
        schema_dirs=schema_dirs,
        store=store,
        tally=tally,
        empty=empty,
        header_failures=header_failures,
        allow_empty_sections=allow_empty_sections,
        warnings=warnings,
        workers=workers,
        chunk_size=chunk_size,
    )
    return StreamValidationResult(passed=report["result"] == "PASS", report=report)


def _bundle_path(source: str | PathLike[str]) -> tuple[Path, Path | None]:
    """Resolve a bundle file and the schema of its registration, if any.

    :param source: Bundle path or registered bundle name.
    :return: The bundle file and its registered schema path.
    :raises BundleNotFoundError: If the source cannot be found.
    """
    path = Path(source)
    if path.is_file():
        return path, None

    if isinstance(source, str) and source in bundle_registry.registered_names():
        registration = bundle_registry.get_registration(source)
        if registration.source.is_file():
            return registration.source, registration.schema

    message = f"Bundle source does not exist: {path}"
    raise BundleNotFoundError(message)


def _is_gzip(path: Path) -> bool:
    """Return whether a file starts with the gzip magic number.

    :param path: File to inspect.
    :return: ``True`` for a gzip-compressed file.
    """
    with path.open("rb") as stream:
        return stream.read(2) == _GZIP_MAGIC


def _bundle_schema(
    schema: str | PathLike[str] | Mapping[str, Any] | None,
    schema_id: str | None,
    schema_files: Mapping[str, SchemaFile],
) -> tuple[Mapping[str, Any], SchemaFile | None]:
    """Find and decode the producer bundle schema.

    :param schema: Schema path or document, if given.
    :param schema_id: Schema ``$id`` to find in ``schema_files``, if given.
    :param schema_files: Local schemas keyed by ``$id``.
    :return: The schema document and, when read from a file, that file.
    :raises BundleNotFoundError: If the schema cannot be found.
    :raises BundleSerializationError: If no schema is available, it is not a
        JSON object, or its ``$id`` differs from ``schema_id``.
    """
    schema_file: SchemaFile | None = None
    if isinstance(schema, Mapping):
        document: Mapping[str, Any] = schema
    elif schema is not None:
        schema_file = _read_bundle_schema_file(Path(schema))
        document = schema_file.contents
    elif schema_id is not None:
        schema_file = schema_files.get(schema_id)
        if schema_file is None:
            message = f"No schema directory contains a schema with $id {schema_id!r}"
            raise BundleNotFoundError(message)
        document = schema_file.contents
    else:
        message = "A bundle JSON Schema is required"
        raise BundleSerializationError(message)

    if schema_id is not None and document.get("$id") != schema_id:
        message = (
            f"Bundle schema $id {document.get('$id')!r} does not match {schema_id!r}"
        )
        raise BundleSerializationError(message)
    return document, schema_file


def _read_bundle_schema_file(path: Path) -> SchemaFile:
    """Read a bundle schema file.

    :param path: Schema file.
    :return: The schema file; its identifier is empty when it has no ``$id``.
    :raises BundleNotFoundError: If the file does not exist.
    :raises BundleSerializationError: If it is not a JSON object.
    """
    try:
        raw = path.read_bytes()
    except OSError as error:
        message = f"Bundle schema does not exist: {path}"
        raise BundleNotFoundError(message) from error
    try:
        document = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        message = f"Invalid JSON in {path}: {error}"
        raise BundleSerializationError(message) from error
    if not isinstance(document, dict):
        message = "A bundle schema must be a JSON object"
        raise BundleSerializationError(message)
    identifier = document.get("$id")
    return SchemaFile(
        identifier=identifier if isinstance(identifier, str) else "",
        path=path,
        sha256=hashlib.sha256(raw).hexdigest(),
        contents=document,
    )


def _compatibility_warnings(schema: Mapping[str, Any]) -> list[str]:
    """Return GKM version-compatibility findings as warnings.

    Streaming validation does not convert records to reference-implementation
    models, so a version mismatch does not fail the report by itself.

    :param schema: Producer bundle JSON Schema.
    :return: Warning messages.
    """
    try:
        check_gkm_version_compatibility(schema)
    except BundleCompatibilityError as error:
        return [str(error)]
    return []


def _record_type(record: Any) -> str:
    """Return a record's ``type`` value, or its JSON type when it has none.

    :param record: Decoded record.
    :return: The type label.
    """
    if isinstance(record, Mapping):
        value = record.get("type")
        return value if isinstance(value, str) else "(no type)"
    return type(record).__name__


def _sidecar_digest(
    bundle_path: Path, sidecar: str | PathLike[str] | None
) -> tuple[str | None, str | None]:
    """Read a published SHA-256 digest from a sidecar file.

    :param bundle_path: Bundle file.
    :param sidecar: Explicit sidecar path, if given.
    :return: The sidecar path and digest, or ``None`` for each when unavailable.
    :raises BundleNotFoundError: If an explicit sidecar does not exist.
    """
    if sidecar is not None:
        path = Path(sidecar)
        if not path.is_file():
            message = f"SHA-256 sidecar does not exist: {path}"
            raise BundleNotFoundError(message)
    else:
        path = bundle_path.with_name(bundle_path.name + ".sha256")
        if not path.is_file():
            return None, None

    tokens = path.read_text(encoding="utf-8").split()
    return str(path), (tokens[0].lower() if tokens else "")


def _distribution_version(name: str) -> str | None:
    """Return an installed distribution's version.

    :param name: Distribution name.
    :return: The version, or ``None`` when it is not installed.
    """
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def _iso(moment: datetime.datetime) -> str:
    """Format a UTC time stamp.

    :param moment: Time to format.
    :return: ISO 8601 text with a ``Z`` suffix.
    """
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _section_schemas(
    schema: Mapping[str, Any],
    section: str,
    store: Mapping[str, Mapping[str, Any]],
    schema_files: Mapping[str, SchemaFile],
    types: collections.Counter[str],
    records: int,
) -> list[dict[str, Any]]:
    """Describe the schemas a section's records are validated against.

    Only the first level is listed: the external ``$ref`` targets of the
    section's record schema, reached directly or through ``oneOf``, ``anyOf``,
    or ``allOf``. Schemas those reference in turn are not listed.

    :param schema: Producer bundle JSON Schema.
    :param section: Section name.
    :param store: Schema contents used for validation, keyed by ``$id``.
    :param schema_files: Local schema files keyed by ``$id``.
    :param types: Record ``type`` counts for the section.
    :param records: Records in the section.
    :return: One entry per referenced schema.
    """
    section_schema = schema_for_pointer(schema, [section])
    if section_schema is None:
        return []
    section_schema = _resolve_local_reference(section_schema, schema)

    record_schemas: list[tuple[str | None, Mapping[str, Any]]] = []
    patterns = section_schema.get("patternProperties")
    if isinstance(patterns, Mapping):
        record_schemas.extend(
            (pattern, node)
            for pattern, node in patterns.items()
            if isinstance(node, Mapping)
        )
    additional = section_schema.get("additionalProperties")
    if isinstance(additional, Mapping):
        record_schemas.append((None, additional))

    entries: list[dict[str, Any]] = []
    for pattern, node in record_schemas:
        resolved = _resolve_local_reference(node, schema)
        combined_by = next(
            (keyword for keyword in _COMBINING_KEYWORDS if keyword in resolved), None
        )
        for reference in schema_references(node, schema):
            contents = store.get(reference)
            local = schema_files.get(reference)
            match = _GKM_SCHEMA_URL.search(reference)
            type_property = (contents or {}).get("properties", {}).get("type", {})
            entries.append(
                {
                    "key_pattern": pattern,
                    "combined_by": combined_by if "$ref" not in resolved else None,
                    "$id": reference,
                    "title": (contents or {}).get("title"),
                    "standard": match.group("standard") if match else None,
                    "version": match.group("version") if match else None,
                    "record_type": type_property.get("const")
                    if isinstance(type_property, Mapping)
                    else None,
                    "source": (
                        "file"
                        if local is not None
                        else "installed model"
                        if contents is not None
                        else None
                    ),
                    "file": str(local.path) if local is not None else None,
                    "file_sha256": local.sha256 if local is not None else None,
                    "resolved": contents is not None,
                }
            )

    record_types = [entry["record_type"] for entry in entries]
    for entry in entries:
        if len(entries) == 1:
            entry["records"] = records
        elif (
            entry["record_type"] is not None
            and record_types.count(entry["record_type"]) == 1
        ):
            entry["records"] = types.get(entry["record_type"], 0)
        else:
            entry["records"] = None
    return entries


def _build_report(
    *,
    started: datetime.datetime,
    finished: datetime.datetime,
    bundle_path: Path,
    url: str | None,
    compressed: bool,
    hashing: _HashingReader,
    sidecar: tuple[str | None, str | None],
    schema_document: Mapping[str, Any],
    schema_file: SchemaFile | None,
    schema_files: Mapping[str, SchemaFile],
    schema_dirs: list[str],
    store: Mapping[str, Mapping[str, Any]],
    tally: _Tally,
    empty: list[str],
    header_failures: int,
    allow_empty_sections: bool,
    warnings: list[str],
    workers: int,
    chunk_size: int,
) -> dict[str, Any]:
    """Assemble the verification report.

    :return: The report as a JSON-compatible dictionary.
    """
    sha256 = hashing.digest.hexdigest()
    sidecar_path, published = sidecar
    sha_ok = None if published is None else published == sha256
    total = sum(tally.records.values())
    failing = sum(tally.failing.values()) + header_failures

    sections = [
        {
            "name": name,
            "records": tally.records[name] + tally.skipped[name],
            "failing": tally.failing[name],
            "validated": name not in tally.skipped,
            "record_types": dict(tally.types[name].most_common()),
            "schemas": _section_schemas(
                schema_document,
                name,
                store,
                schema_files,
                tally.types[name],
                tally.records[name],
            ),
        }
        for name in tally.order
    ]

    checks = _const_checks(schema_document, tally.headers)
    required = schema_document.get("required")
    if isinstance(required, list) and required:
        present = set(tally.headers) | set(tally.order)
        missing = [name for name in required if name not in present]
        checks.append(
            {
                "check": "every top-level property the schema requires is present",
                "missing": missing,
                "result": "FAIL" if missing else "PASS",
            }
        )
    checks.extend(
        [
            {
                "check": "sha256 of the bytes read equals the published .sha256 sidecar",
                "expected": published,
                "found": sha256,
                "result": "NOT CHECKED (no sidecar)"
                if sha_ok is None
                else ("PASS" if sha_ok else "FAIL"),
            },
            {
                "check": "every section has at least one record",
                "empty_sections": empty,
                "result": "PASS"
                if not empty
                else ("ALLOWED" if allow_empty_sections else "FAIL"),
            },
            {
                "check": "every record validates against the bundle schema",
                "records": total,
                "failing": failing - header_failures,
                "result": "PASS" if failing == header_failures else "FAIL",
            },
            {
                "check": "top-level values and empty sections validate against the bundle schema",
                "result": "FAIL" if header_failures else "PASS",
            },
            {
                "check": "every section validated (none skipped)",
                "skipped": dict(tally.skipped),
                "result": "FAIL" if tally.skipped else "PASS",
            },
        ]
    )

    if sha_ok is None:
        warnings.append(
            "no .sha256 sidecar was available; the file's integrity was not "
            "checked against a published digest"
        )
    if tally.with_pointers:
        warnings.append(
            f"{tally.with_pointers:,d} records contain bundle-local JSON Pointers "
            "(#/...); streaming validation checks them verbatim and does not "
            "resolve or expand them"
        )
    if tally.skipped:
        warnings.append(
            "sections counted but not validated: " + ", ".join(tally.skipped)
        )
    unresolved = sorted(
        {
            entry["$id"]
            for section in sections
            for entry in section["schemas"]
            if not entry["resolved"]
        }
    )
    if unresolved:
        warnings.append(
            "schemas not available locally (add a schema directory): "
            + ", ".join(unresolved)
        )

    passed = total > 0 and all(check["result"] != "FAIL" for check in checks)
    return {
        "report": "GKM bundle validation report",
        "report_version": REPORT_VERSION,
        "result": "PASS" if passed else "FAIL",
        "started_at": _iso(started),
        "finished_at": _iso(finished),
        "duration_seconds": round((finished - started).total_seconds()),
        "bundle": {
            "file": bundle_path.name,
            "url": url,
            "compression": "gzip" if compressed else None,
            "size_bytes": hashing.size,
            "sha256": sha256,
            "sidecar": sidecar_path,
            "published_sha256": published,
            "top_level_values": {
                key: value
                for key, value in tally.headers.items()
                if not isinstance(value, (Mapping, list))
            },
        },
        "validator": {
            "tool": "GA4GH GKM Toolkit (ga4gh.gkm)",
            "function": "ga4gh.gkm.bundles.validate_bundle_stream",
            "mode": (
                "streaming; every record validated verbatim with "
                "validate_bundle_schema, in chunks wrapped as one-section bundles"
            ),
            "versions": {
                name: _distribution_version(name) for name in _REPORTED_DISTRIBUTIONS
            }
            | {"python": platform.python_version()},
            "workers": workers,
            "chunk_size": chunk_size,
        },
        "schemas": {
            "bundle_schema_id": schema_document.get("$id"),
            "bundle_schema_file": str(schema_file.path) if schema_file else None,
            "bundle_schema_sha256": schema_file.sha256 if schema_file else None,
            "schema_dirs": schema_dirs,
            "schema_files_loaded": len(schema_files),
        },
        "totals": {"sections": len(sections), "records": total, "failing": failing},
        "sections": sections,
        "checks": checks,
        "warnings": warnings,
        "failures_sample": tally.failures,
    }


def _const_checks(
    schema: Mapping[str, Any], headers: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Check top-level values against the schema's ``const`` values.

    :param schema: Producer bundle JSON Schema.
    :param headers: Top-level values that are not sections.
    :return: One check per top-level property with a ``const``.
    """
    checks = []
    properties = schema.get("properties")
    if not isinstance(properties, Mapping):
        return checks
    required = schema.get("required") or []
    for name, node in properties.items():
        if not isinstance(node, Mapping) or "const" not in node:
            continue
        expected = node["const"]
        if name in headers:
            result = "PASS" if headers[name] == expected else "FAIL"
        else:
            result = "FAIL" if name in required else "NOT CHECKED (absent)"
        checks.append(
            {
                "check": f"bundle {name} equals the schema's const",
                "expected": expected,
                "found": headers.get(name),
                "result": result,
            }
        )
    return checks


def render_report_markdown(report: Mapping[str, Any]) -> str:
    """Render a verification report as a Markdown summary.

    :param report: Report from :meth:`StreamValidationResult.to_dict`.
    :return: The Markdown document.
    """
    bundle = report["bundle"]
    totals = report["totals"]
    validator = report["validator"]
    schemas = report["schemas"]
    sha_check = next(
        check for check in report["checks"] if check["check"].startswith("sha256")
    )
    sha_note = {
        "PASS": "matches the published sidecar",
        "FAIL": "DOES NOT MATCH the published sidecar",
    }.get(sha_check["result"], "no sidecar check")
    top_level = ", ".join(
        f"`{key}` = `{value}`" for key, value in bundle["top_level_values"].items()
    )
    schema_file = (
        f" (`{schemas['bundle_schema_file']}`)" if schemas["bundle_schema_file"] else ""
    )

    lines = [
        f"# Validation report: `{bundle['file']}`",
        "",
        f"**Result: {report['result']}** · {totals['records']:,d} records in "
        f"{totals['sections']} sections · {totals['failing']:,d} failing",
        "",
        "| | |",
        "| --- | --- |",
        f"| Bundle | `{bundle['file']}` ({bundle['size_bytes']:,d} bytes) |",
        f"| Published at | {bundle['url'] or '(not given)'} |",
        f"| sha256 | `{bundle['sha256']}` ({sha_note}) |",
        f"| Top-level values | {top_level or '(none)'} |",
        f"| Validator | GA4GH GKM Toolkit `ga4gh.gkm` "
        f"{validator['versions'].get('ga4gh.gkm')}, every record |",
        f"| Bundle schema | `{schemas['bundle_schema_id']}`{schema_file} |",
        f"| Run | {report['started_at']} → {report['finished_at']} "
        f"({report['duration_seconds']:,d} s, {validator['workers']} workers) |",
        "",
        "| Section | Records | Failing |",
        "| --- | ---: | ---: |",
    ]
    lines += [
        f"| `{section['name']}` | {section['records']:,d} | {section['failing']:,d} |"
        for section in report["sections"]
    ]
    lines += [
        "",
        "**Schemas applied, by section.** Each section's records are validated "
        "against the schema(s) the bundle schema names for that section "
        "(`$ref`); the schemas those reference in turn are not listed. Where a "
        "section names several, they combine as shown (`oneOf`: each record must "
        "match exactly one; `anyOf`: at least one; `allOf`: all), and the count "
        "is the records whose `type` is that schema's.",
        "",
        "| Section | Schema | Standard | Version | Combined by | Records |",
        "| --- | --- | --- | --- | --- | ---: |",
    ]
    for section in report["sections"]:
        lines += _schema_rows(section)
    lines += ["", "**Checks**", ""]
    lines += [f"- {check['result']}: {check['check']}" for check in report["checks"]]
    lines += [
        "",
        "**Warnings:** "
        + ("; ".join(report["warnings"]) if report["warnings"] else "none"),
    ]
    if report["failures_sample"]:
        lines += ["", "**First failures**", ""]
        lines += [f"- `{failure}`" for failure in report["failures_sample"][:20]]
    return "\n".join(lines) + "\n"


def _schema_rows(section: Mapping[str, Any]) -> list[str]:
    """Render one section's rows of the schemas table.

    :param section: Section entry from the report.
    :return: Markdown table rows.
    """
    entries = section["schemas"]
    if not entries:
        return [f"| `{section['name']}` | (no schema reference) | | | | {_NO_COUNT} |"]

    single = len(entries) == 1
    types_note = ""
    if single and section["record_types"]:
        types_note = (
            " (" + ", ".join(f"`{name}`" for name in section["record_types"]) + ")"
        )
    rows = []
    matched = set()
    for entry in entries:
        count = entry["records"]
        if count is not None and not single:
            matched.add(entry["record_type"])
        title = entry["title"] or entry["$id"].rsplit("/", 1)[-1]
        rows.append(
            f"| `{section['name']}` | [{title}]({entry['$id']}) | "
            f"{entry['standard'] or ''} | {entry['version'] or ''} | "
            f"{'' if single else (entry['combined_by'] or '')} | "
            f"{f'{count:,d}' if count is not None else _NO_COUNT}{types_note} |"
        )
    other = {
        name: count
        for name, count in section["record_types"].items()
        if not single and name not in matched
    }
    if other:
        rows.append(
            f"| `{section['name']}` | *records whose `type` names none of the "
            "above* | | | | "
            + ", ".join(f"`{name}` {count:,d}" for name, count in other.items())
            + " |"
        )
    return rows
