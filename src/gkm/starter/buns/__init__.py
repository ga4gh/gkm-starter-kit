"""Load, inspect, and catalog GKM buns."""

from .catalog import BunCatalog, BunRegistration, catalog
from .compatibility import check_gkm_version_compatibility, supported_gkm_versions
from .errors import (
    BunCompatibilityError,
    BunError,
    BunFormatError,
    BunNotFoundError,
    BunReferenceError,
)
from .loading import BunSource, load_bun, load_buns
from .models import Bun, BunCollection


def registered_names() -> tuple[str, ...]:
    """Return the names of registered buns.

    :return: Registered names in alphabetical order.
    """
    return catalog.registered_names()


def get_registration(name: str) -> BunRegistration:
    """Return a bun registration by name.

    :param name: Registered bun name.
    :return: The matching bun registration.
    :raises BunNotFoundError: If ``name`` is not registered.
    """
    return catalog.get_registration(name)


def register(registration: BunRegistration, *, replace: bool = False) -> None:
    """Register a named bun.

    :param registration: Bun name and source information.
    :param replace: Replace an existing registration with the same name.
    :raises ValueError: If the name exists and ``replace`` is false.
    """
    catalog.register(registration, replace=replace)


__all__ = [
    "Bun",
    "BunCatalog",
    "BunCollection",
    "BunCompatibilityError",
    "BunError",
    "BunFormatError",
    "BunNotFoundError",
    "BunReferenceError",
    "BunRegistration",
    "BunSource",
    "catalog",
    "check_gkm_version_compatibility",
    "get_registration",
    "load_bun",
    "load_buns",
    "register",
    "registered_names",
    "supported_gkm_versions",
]
