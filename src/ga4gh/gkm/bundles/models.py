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
        """Resolve an RFC 6901 JSON Pointer into this bundle.

        :param pointer: Bundle-local pointer beginning with ``#/``.
        :return: The referenced value.
        :raises BundleReferenceError: If the pointer is invalid or cannot be resolved.
        """
        if not pointer.startswith("#/"):
            message = f"Expected a bundle-local JSON Pointer, got {pointer!r}"
            raise BundleReferenceError(message)

        value: Any = self

        for raw_part in pointer[2:].split("/"):
            part = raw_part.replace("~1", "/").replace("~0", "~")

            try:
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

    def _dereference_value(self, value: Any, *, trail: tuple[str, ...]) -> Any:
        """Replace local pointers below a value with inline values.

        :param value: Value to traverse.
        :param trail: Pointers currently being resolved, used to detect cycles.
        :return: A JSON-compatible value with local pointers replaced inline.
        Cycle-closing pointers remain referenced because JSON cannot represent a
        cyclic inline value.
        """
        if isinstance(value, str) and value.startswith("#/"):
            if value in trail:
                return value

            return self._dereference_value(
                self.resolve(value),
                trail=(*trail, value),
            )

        if isinstance(value, BaseModel):
            value = value.model_dump(mode="json", exclude_none=True)

        if isinstance(value, Mapping):
            return {
                key: self._dereference_value(item, trail=trail)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [self._dereference_value(item, trail=trail) for item in value]

        return value

    def dereference(self, value: Any | None = None) -> Any:
        """Return a value with all reachable local references replaced inline.

        The complete bundle is used when ``value`` is omitted. The bundle itself remains
        referenced.

        Cycle-closing pointers remain referenced because JSON cannot represent a
        cyclic inline value.

        :param value: Value from this bundle to dereference, or ``None`` for the
            complete bundle.
        :return: A JSON-compatible, inline representation of the value.
        """
        target = self.to_dict() if value is None else value
        return self._dereference_value(target, trail=())

    def to_dict(self) -> dict[str, Any]:
        """Serialize the bundle to JSON-compatible Python values.

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
