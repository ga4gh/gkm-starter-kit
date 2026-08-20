"""Catalog of named buns."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from .errors import BunNotFoundError


@dataclass(frozen=True, slots=True)
class BunRegistration:
    """Associate a bun name with its source and schema.

    :param name: Public name used to load the bun.
    :param source: Path to its serialized document.
    :param schema: Path to its producer JSON Schema, when available.
    :param producer: Organization that produced the data, when known.
    :param description: Short description of the bun, when available.
    """

    name: str
    source: Path
    schema: Path | None = None
    producer: str | None = None
    description: str | None = None


class BunCatalog:
    """Mutable catalog of named bun sources."""

    def __init__(self) -> None:
        """Create an empty bun catalog."""
        self._registrations: dict[str, BunRegistration] = {}

    def register(self, registration: BunRegistration, *, replace: bool = False) -> None:
        """Register a named bun.

        :param registration: Bun name and source information.
        :param replace: Replace an existing registration with the same name.
        :raises ValueError: If the name exists and ``replace`` is false.
        """
        if registration.name in self._registrations and not replace:
            message = f"Bun {registration.name!r} is already registered"
            raise ValueError(message)

        self._registrations[registration.name] = registration

    def registered_names(self) -> tuple[str, ...]:
        """Return registered bun names.

        :return: Registered names in alphabetical order.
        """
        return tuple(sorted(self._registrations))

    def get_registration(self, name: str) -> BunRegistration:
        """Return a bun registration by name.

        :param name: Registered bun name.
        :return: The matching registration.
        :raises BunNotFoundError: If ``name`` is not registered.
        """
        try:
            return self._registrations[name]
        except KeyError as error:
            available = ", ".join(self.registered_names()) or "none"
            message = f"Unknown bun {name!r}. Available buns: {available}."

            raise BunNotFoundError(message) from error


catalog = BunCatalog()
