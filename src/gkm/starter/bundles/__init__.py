"""Load, inspect, and register GKM bundles."""

from .compatibility import check_gkm_version_compatibility, supported_gkm_versions
from .errors import (
    BundleCollectionNotFoundError,
    BundleCompatibilityError,
    BundleConflictError,
    BundleError,
    BundleNotFoundError,
    BundleObjectNotFoundError,
    BundleReferenceError,
    BundleSerializationError,
    BundleValidationError,
)
from .loading import BundleSource, load_bundle, load_bundles
from .models import Bundle, BundleCollection
from .registry import BundleRegistration, BundleRegistry, registry


def registered_names() -> tuple[str, ...]:
    """Return the names of registered bundles.

    :return: Registered names in alphabetical order.
    """
    return registry.registered_names()


def get_registration(name: str) -> BundleRegistration:
    """Return a bundle registration by name.

    :param name: Registered bundle name.
    :return: The matching bundle registration.
    :raises BundleNotFoundError: If ``name`` is not registered.
    """
    return registry.get_registration(name)


def register(registration: BundleRegistration, *, replace: bool = False) -> None:
    """Register a named bundle.

    :param registration: Bundle name and source information.
    :param replace: Replace an existing registration with the same name.
    :raises BundleConflictError: If the name exists and ``replace`` is false.
    """
    registry.register(registration, replace=replace)


__all__ = [
    "Bundle",
    "BundleCollection",
    "BundleCollectionNotFoundError",
    "BundleCompatibilityError",
    "BundleConflictError",
    "BundleError",
    "BundleNotFoundError",
    "BundleObjectNotFoundError",
    "BundleReferenceError",
    "BundleRegistration",
    "BundleRegistry",
    "BundleSerializationError",
    "BundleSource",
    "BundleValidationError",
    "check_gkm_version_compatibility",
    "get_registration",
    "load_bundle",
    "load_bundles",
    "register",
    "registered_names",
    "registry",
    "supported_gkm_versions",
]
