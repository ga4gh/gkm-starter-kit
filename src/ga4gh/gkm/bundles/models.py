"""In-memory bundle containers."""

# ruff: noqa: ANN401

from __future__ import annotations

import json
from collections.abc import Iterator, KeysView, Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .errors import (
    BundleCollectionNotFoundError,
    BundleObjectNotFoundError,
    BundleReferenceError,
    BundleSerializationError,
)


def _to_json_value(value: Any) -> Any:
    """Convert reference-library models and containers to JSON values.

    :param value: Value to serialize.
    :return: A JSON-compatible value.
    """
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", exclude_none=True)

    if isinstance(value, Mapping):
        return {key: _to_json_value(item) for key, item in value.items()}

    if isinstance(value, list):
        return [_to_json_value(item) for item in value]

    return value


class BundleCollection(Mapping[str, Any]):
    """A named, keyed collection within a :class:`Bundle`.

    :param name: Collection name from the bundle.
    :param values: Objects keyed by their identifiers.
    """

    def __init__(self, name: str, values: Mapping[str, Any]) -> None:
        """Initialize a bundle collection.

        :param name: Collection name from the bundle.
        :param values: Objects keyed by their identifiers.
        """
        self.name = name
        self._values = dict(values)

    def __getitem__(self, key: str) -> Any:
        """Return an object by identifier.

        :param key: Object identifier.
        :return: The stored object.
        :raises BundleObjectNotFoundError: If ``key`` is absent.
        """
        try:
            return self._values[key]
        except KeyError as error:
            message = f"Unknown identifier {key!r} in collection {self.name!r}"
            raise BundleObjectNotFoundError(message) from error

    def __iter__(self) -> Iterator[str]:
        """Iterate over object identifiers.

        :return: An iterator over identifiers.
        """
        return iter(self._values)

    def __len__(self) -> int:
        """Return the number of objects in the collection.

        :return: Collection size.
        """
        return len(self._values)

    def keys(self) -> KeysView[str]:
        """Return the object identifiers in the collection.

        :return: A view of the collection's object identifiers.
        """
        return self._values.keys()

    def __repr__(self) -> str:
        """Return a concise representation of the collection.

        :return: Collection name and size.
        """
        return f"BundleCollection(name={self.name!r}, size={len(self)})"


class Bundle(Mapping[str, BundleCollection]):
    """Represent a GKM Bundle in memory.

    Producer-defined collection names are preserved and can be accessed through
    mapping syntax, attribute access, or :meth:`collection`.

    :param collections: Named object collections in the bundle.
    :param metadata: Bundle and provenance metadata.
    :param extras: Top-level values that are not object collections.
    :param name: Registered or inferred bundle name.
    """

    def __init__(
        self,
        collections: Mapping[str, BundleCollection],
        *,
        metadata: Mapping[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
        name: str | None = None,
    ) -> None:
        """Initialize a bundle.

        :param collections: Named object collections in the bundle.
        :param metadata: Bundle and provenance metadata.
        :param extras: Top-level values that are not object collections.
        :param name: Registered or inferred bundle name.
        """
        self.name = name
        self.metadata = dict(metadata or {})
        self.collections = dict(collections)
        self.extras = dict(extras or {})

    def __getitem__(self, name: str) -> BundleCollection:
        """Return a collection by name.

        :param name: Collection name.
        :return: The matching collection.
        :raises BundleCollectionNotFoundError: If ``name`` is absent.
        """
        try:
            return self.collections[name]
        except KeyError as error:
            message = f"Unknown collection {name!r}"
            raise BundleCollectionNotFoundError(message) from error

    def __iter__(self) -> Iterator[str]:
        """Iterate over collection names.

        :return: An iterator over collection names.
        """
        return iter(self.collections)

    def __len__(self) -> int:
        """Return the number of collections.

        :return: Collection count.
        """
        return len(self.collections)

    def collection_names(self) -> tuple[str, ...]:
        """Return the collection names in document order.

        :return: Names of the collections exposed by this bundle.
        """
        return tuple(self.collections)

    def __getattr__(self, name: str) -> BundleCollection:
        """Provide attribute access to named collections.

        :param name: Collection name.
        :return: The matching collection.
        :raises BundleCollectionNotFoundError: If ``name`` is not a collection.
        """
        return self[name]

    def collection(self, name: str) -> BundleCollection:
        """Return a collection by name.

        :param name: Collection name.
        :return: The matching collection.
        :raises BundleCollectionNotFoundError: If ``name`` is absent.
        """
        return self[name]

    def resolve(self, pointer: str) -> Any:
        """Resolve an RFC 6901 JSON Pointer into the bundle.

        Use this for one pointer; use :meth:`normalize` to expand references
        recursively.

        :param pointer: Bundle-local pointer beginning with ``#/``.
        :return: The referenced value.
        :raises BundleReferenceError: If the pointer is invalid or cannot be resolved.
        """
        if not pointer.startswith("#/"):
            message = f"Expected a bundle-local JSON Pointer, got {pointer!r}"
            raise BundleReferenceError(message)

        value: Any = self

        for raw_part in pointer[2:].split("/"):
            # Decode each RFC 6901 path segment; e.g. "a~1b" addresses "a/b".
            part = raw_part.replace("~1", "/").replace("~0", "~")

            try:
                # Traverse bundles, sequences, mappings, and model attributes.
                if isinstance(value, Bundle):
                    value = value[part]
                elif isinstance(value, (list, tuple)):
                    value = value[int(part)]
                elif isinstance(value, Mapping):
                    value = value[part]
                else:
                    value = getattr(value, part)
            except (
                AttributeError,
                IndexError,
                KeyError,
                TypeError,
                ValueError,
            ) as error:
                message = f"Could not resolve bundle reference {pointer!r}"
                raise BundleReferenceError(message) from error

        return value

    def _normalize_value(self, value: Any, *, trail: tuple[str, ...]) -> Any:
        """Replace local pointers below a value with inline values.

        :param value: Value to traverse.
        :param trail: Pointers currently being resolved, used to detect cycles.
        :return: A JSON-compatible value with local pointers replaced inline.
            Cycle-closing pointers remain referenced because JSON cannot represent a
            cyclic inline value.
        """
        if isinstance(value, str) and value.startswith("#/"):
            # Expand local pointers recursively; for example, "#/a/1" can
            # resolve to an object containing another pointer, "#/b/2".
            if value in trail:
                # Keep the closing pointer because inline JSON cannot be cyclic.
                return value

            return self._normalize_value(
                self.resolve(value),
                trail=(*trail, value),
            )

        if isinstance(value, BaseModel):
            value = value.model_dump(mode="json", exclude_none=True)

        if isinstance(value, Mapping):
            return {
                key: self._normalize_value(item, trail=trail)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [self._normalize_value(item, trail=trail) for item in value]

        return value

    def normalize(self, value: Any | None = None) -> Any:
        """Normalize bundle content for use outside the serialized bundle.

        Bundle-local pointers are expanded recursively; cyclic pointers remain
        pointers. Omitting ``value`` normalizes the complete bundle.

        :param value: Bundle value to normalize, or ``None`` for the complete
            bundle.
        :return: JSON-compatible normalized content.
        :raises BundleReferenceError: If a local reference cannot be resolved.
        """
        target = self.to_dict() if value is None else value
        return self._normalize_value(target, trail=())

    def denormalize(self, value: Any) -> Any:
        """Replace embedded bundle objects with local JSON Pointer references.

        Embedded objects matching bundle objects are replaced by local pointers;
        unknown producer content is preserved. Exact content matches take
        precedence over the optional ``id``/``type`` identity fallback.

        :param value: Normalized JSON-compatible value.
        :return: Content using bundle-local references where possible.
        :raises BundleSerializationError: If ``value`` cannot be represented as
            JSON-compatible content.
        """

        def reference_for(item: Mapping[str, Any]) -> str | None:
            """Return the bundle pointer for a recognized nested object.

            Exact matches take precedence over identity matches.

            :param item: Mapping to look up.
            :return: Local pointer, or ``None`` when the item is not recognized.
            """
            serialized = json.dumps(item, sort_keys=True)
            pointer = exact_references.get(serialized)

            if pointer is not None:
                return pointer

            return identity_references.get((item.get("id"), item.get("type")))

        def replace(item: Any, *, root: bool = False) -> Any:
            """Recursively replace embedded bundle objects with pointers.

            The root stays an object document; only nested mappings can become
            pointers. Lists are traversed and other values are unchanged.

            :param item: JSON-compatible value currently being traversed.
            :param root: Whether ``item`` is the value supplied by the caller.
            :return: Value with recognized nested objects replaced by pointers.
            """
            if isinstance(item, Mapping):
                if not root:
                    pointer = reference_for(item)
                    if pointer is not None:
                        return pointer

                # Keep an individual export as an object; nested matches become
                # pointers, e.g. {"child": {"id": "1", "type": "Thing"}}
                # becomes {"child": "#/things/1"}.
                return {key: replace(child) for key, child in item.items()}

            if isinstance(item, list):
                return [replace(child) for child in item]

            return item

        try:
            json.dumps(value)
        except (TypeError, ValueError) as error:
            message = f"Content cannot be denormalized as JSON: {error}"
            raise BundleSerializationError(message) from error

        # Build lookups once so nested objects do not require repeated scans.
        # Example: {"id": "1", "type": "Thing"} -> "#/things/1".
        exact_references = {
            json.dumps(_to_json_value(obj), sort_keys=True): f"#/{name}/{key}"
            for name, collection in self.collections.items()
            for key, obj in collection.items()
        }

        # Prefer complete matches; use stable id/type when extra fields differ.
        # Example: {"id": "1", "type": "Thing", "description": "..."}
        # still maps to "#/things/1".
        identity_references = {
            (serialized.get("id"), serialized.get("type")): pointer
            for serialized, pointer in (
                (json.loads(serialized), pointer)
                for serialized, pointer in exact_references.items()
            )
            if serialized.get("id") is not None and serialized.get("type") is not None
        }

        return replace(value, root=True)

    def export(self, value: Any | None = None, *, deep: bool = False) -> Any:
        """Export a complete bundle or an individual object.

        ``deep=False`` preserves local pointers; ``deep=True`` expands them.
        Omitting ``value`` exports the complete bundle. The result is validated
        as JSON-compatible.

        :param value: Object or content to export, or ``None`` for the bundle.
        :param deep: Include reachable referenced content instead of preserving
            local references.
        :return: JSON-compatible exported content.
        :raises BundleSerializationError: If content is not JSON-compatible.
        """
        if value is None:
            # A bundle export starts from the complete shallow document.
            exported = self.to_dict()
            if deep:
                # Deep export expands its local pointers for standalone use.
                exported = self.normalize(exported)
        else:
            # An object export first restores pointers for known nested objects.
            exported = self.denormalize(value)
            if deep:
                # Then optionally expand those pointers again for deep output.
                exported = self.normalize(exported)

        try:
            json.dumps(exported)
        except (TypeError, ValueError) as error:
            message = f"Exported content is not valid JSON: {error}"
            raise BundleSerializationError(message) from error

        return exported

    def to_dict(self) -> dict[str, Any]:
        """Return the complete bundle as shallow Python values.

        This preserves local pointers and does not write a file.

        :return: The complete serialized bundle.
        """
        document = {
            name: _to_json_value(collection)
            for name, collection in self.collections.items()
        }

        if self.metadata:
            document["metadata"] = _to_json_value(self.metadata)

        document.update(_to_json_value(self.extras))

        return document

    def write(
        self,
        destination: str | Path,
        *,
        serialization: str = "json",
        indent: int | None = 2,
    ) -> None:
        """Write the bundle to a file.

        Writing preserves collection names, identifiers, local references,
        metadata, and producer-specific values, but the result may not be
        byte-for-byte identical to the input. Output is not validated against
        the producer's schema.

        :param destination: Output file path.
        :param serialization: Output serialization. Only ``"json"`` is supported.
        :param indent: Number of spaces used to indent JSON, or ``None`` for compact
            output.
        :raises BundleSerializationError: If ``serialization`` is unsupported.
        """
        if serialization != "json":
            message = f"Unsupported serialization {serialization!r}; expected 'json'"
            raise BundleSerializationError(message)

        try:
            serialized = json.dumps(self.to_dict(), indent=indent) + "\n"
        except (TypeError, ValueError) as error:
            message = (
                f"Bundle contains a value that cannot be serialized as JSON: {error}"
            )
            raise BundleSerializationError(message) from error

        Path(destination).write_text(serialized, encoding="utf-8")

    def __repr__(self) -> str:
        """Return a concise representation of the bundle.

        :return: Bundle name and collection count.
        """
        return f"Bundle(name={self.name!r}, collections={len(self)})"
