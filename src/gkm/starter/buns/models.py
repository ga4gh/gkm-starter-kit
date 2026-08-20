"""In-memory bun containers."""

# ruff: noqa: ANN401

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .errors import BunFormatError, BunReferenceError


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


class BunCollection(Mapping[str, Any]):
    """A named, keyed collection within a :class:`Bun`.

    :param name: Collection name from the bun document.
    :param values: Objects keyed by their identifiers.
    """

    def __init__(self, name: str, values: Mapping[str, Any]) -> None:
        """Initialize a bun collection.

        :param name: Collection name from the bun document.
        :param values: Objects keyed by their identifiers.
        """
        self.name = name
        self._values = dict(values)

    def __getitem__(self, key: str) -> Any:
        """Return an object by identifier.

        :param key: Object identifier.
        :return: The stored object.
        :raises KeyError: If ``key`` is absent.
        """
        return self._values[key]

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

    def __repr__(self) -> str:
        """Return a concise representation of the collection.

        :return: Collection name and size.
        """
        return f"BunCollection(name={self.name!r}, size={len(self)})"


class Bun(Mapping[str, BunCollection]):
    """Represent a GKM Bundle in memory.

    :param collections: Named object collections in the bundle.
    :param metadata: Bundle format and provenance metadata.
    :param extras: Top-level values that are not object collections.
    :param name: Registered or inferred bun name.
    """

    def __init__(
        self,
        collections: Mapping[str, BunCollection],
        *,
        metadata: Mapping[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
        name: str | None = None,
    ) -> None:
        """Initialize a bun.

        :param collections: Named object collections in the bundle.
        :param metadata: Bundle format and provenance metadata.
        :param extras: Top-level values that are not object collections.
        :param name: Registered or inferred bun name.
        """
        self.name = name
        self.metadata = dict(metadata or {})
        self.collections = dict(collections)
        self.extras = dict(extras or {})

    def __getitem__(self, name: str) -> BunCollection:
        """Return a collection by name.

        :param name: Collection name.
        :return: The matching collection.
        :raises KeyError: If ``name`` is absent.
        """
        return self.collections[name]

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

        :return: Names of the collections exposed by this bun.
        """
        return tuple(self.collections)

    def __getattr__(self, name: str) -> BunCollection:
        """Provide attribute access to named collections.

        :param name: Collection name.
        :return: The matching collection.
        :raises AttributeError: If ``name`` is not a collection.
        """
        try:
            return self.collections[name]
        except KeyError as error:
            raise AttributeError(name) from error

    def collection(self, name: str) -> BunCollection:
        """Return a collection by name.

        :param name: Collection name.
        :return: The matching collection.
        :raises KeyError: If ``name`` is absent.
        """
        return self.collections[name]

    def resolve(self, pointer: str) -> Any:
        """Resolve an RFC 6901 JSON Pointer into this bun.

        :param pointer: Bun-local pointer beginning with ``#/``.
        :return: The referenced value.
        :raises BunReferenceError: If the pointer is invalid or cannot be resolved.
        """
        if not pointer.startswith("#/"):
            message = f"Expected a bun-local JSON Pointer, got {pointer!r}"
            raise BunReferenceError(message)

        value: Any = self

        for raw_part in pointer[2:].split("/"):
            part = raw_part.replace("~1", "/").replace("~0", "~")

            try:
                if isinstance(value, Bun):
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
                message = f"Could not resolve bun reference {pointer!r}"
                raise BunReferenceError(message) from error

        return value

    def unwrap(self, pointer: str) -> Any:
        """Unwrap a bun-local reference and return its target.

        ``unwrap`` is the bakery-themed equivalent of :meth:`resolve`.

        :param pointer: Bun-local pointer beginning with ``#/``.
        :return: The referenced value.
        :raises BunReferenceError: If the pointer is invalid or cannot be resolved.
        """
        return self.resolve(pointer)

    def _unwrap_value(self, value: Any, *, trail: tuple[str, ...]) -> Any:
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
            return self._unwrap_value(
                self.resolve(value),
                trail=(*trail, value),
            )

        if isinstance(value, BaseModel):
            value = value.model_dump(mode="json", exclude_none=True)

        if isinstance(value, Mapping):
            return {
                key: self._unwrap_value(item, trail=trail)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [self._unwrap_value(item, trail=trail) for item in value]

        return value

    def unwrap_all(self, value: Any | None = None) -> Any:
        """Return a value with all reachable local references replaced inline.

        The complete bun is used when ``value`` is omitted. The bun itself remains
        referenced.

        Cycle-closing pointers remain referenced because JSON cannot represent a
        cyclic inline value.

        :param value: Value from this bun to unwrap, or ``None`` for the complete bun.
        :return: A JSON-compatible, inline representation of the value.
        """
        target = self.to_dict() if value is None else value
        return self._unwrap_value(target, trail=())

    def dereference(self) -> dict[str, Any]:
        """Return the complete bun with local references replaced inline.

        ``dereference`` is the plain-language equivalent of :meth:`unwrap_all`.

        :return: A JSON-compatible, inline representation of the bun.
        """
        return self.unwrap_all()

    def to_dict(self) -> dict[str, Any]:
        """Serialize the bun to JSON-compatible Python values.

        :return: The complete bun document.
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
        """Write the bun to a file.

        :param destination: Output file path.
        :param serialization: Output serialization. Only ``"json"`` is supported.
        :param indent: Number of spaces used to indent JSON, or ``None`` for compact
            output.
        :raises BunFormatError: If ``serialization`` is unsupported.
        """
        if serialization != "json":
            message = f"Unsupported serialization {serialization!r}; expected 'json'"
            raise BunFormatError(message)

        Path(destination).write_text(
            json.dumps(self.to_dict(), indent=indent) + "\n",
            encoding="utf-8",
        )

    def bake(
        self,
        destination: str | Path,
        *,
        indent: int | None = 2,
    ) -> None:
        """Bake the bun into a JSON file.

        ``bake`` is the bakery-themed equivalent of :meth:`write`.

        :param destination: Output file path.
        :param indent: Number of spaces used to indent JSON, or ``None`` for compact
            output.
        """
        self.write(destination, serialization="json", indent=indent)

    def __repr__(self) -> str:
        """Return a concise representation of the bun.

        :return: Bun name and collection count.
        """
        return f"Bun(name={self.name!r}, collections={len(self)})"
