"""Registry of named bundles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from .errors import BundleNotFoundError


@dataclass(frozen=True, slots=True)
class BundleRegistration:
    """Associate a bundle name with its source and schema.

    :param name: Public name used to load the bundle.
    :param source: Path to its serialized document.
    :param schema: Path to its producer JSON Schema, when available.
    :param producer: Organization that produced the data, when known.
    :param description: Short description of the bundle, when available.
    """

    name: str
    source: Path
    schema: Path | None = None
    producer: str | None = None
    description: str | None = None


class BundleRegistry:
    """Mutable registry of named bundle sources."""

    def __init__(self) -> None:
        """Create an empty bundle registry."""
        self._registrations: dict[str, BundleRegistration] = {}

    def register(
        self, registration: BundleRegistration, *, replace: bool = False
    ) -> None:
        """Register a named bundle.

        :param registration: Bundle name and source information.
        :param replace: Replace an existing registration with the same name.
        :raises ValueError: If the name exists and ``replace`` is false.
        """
        if registration.name in self._registrations and not replace:
            message = f"Bundle {registration.name!r} is already registered"
            raise ValueError(message)

        self._registrations[registration.name] = registration

    def registered_names(self) -> tuple[str, ...]:
        """Return registered bundle names.

        :return: Registered names in alphabetical order.
        """
        return tuple(sorted(self._registrations))

    def get_registration(self, name: str) -> BundleRegistration:
        """Return a bundle registration by name.

        :param name: Registered bundle name.
        :return: The matching registration.
        :raises BundleNotFoundError: If ``name`` is not registered.
        """
        try:
            return self._registrations[name]
        except KeyError as error:
            available = ", ".join(self.registered_names()) or "none"
            message = f"Unknown bundle {name!r}. Available bundles: {available}."

            raise BundleNotFoundError(message) from error


registry = BundleRegistry()
