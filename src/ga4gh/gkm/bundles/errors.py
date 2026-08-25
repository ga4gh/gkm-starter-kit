"""Exceptions raised by the bundle API."""


class BundleError(Exception):
    """Base class for bundle-related errors."""


class BundleNotFoundError(BundleError):
    """Raised when a bundle source cannot be found."""


class BundleCollectionNotFoundError(BundleError, AttributeError, KeyError):
    """Raised when a bundle does not contain a requested collection."""


class BundleObjectNotFoundError(BundleError, KeyError):
    """Raised when a collection does not contain a requested object."""


class BundleSerializationError(BundleError):
    """Raised when a bundle's serialization or serialized content is unsupported."""


class BundleCompatibilityError(BundleError):
    """Raised when a bundle schema is incompatible with installed GKM models."""


class BundleConflictError(BundleError, ValueError):
    """Raised when bundle names conflict in a registry or loaded collection."""


class BundleValidationError(BundleError):
    """Raised when a bundle object fails reference-model validation."""


class BundleReferenceError(BundleError):
    """Raised when a bundle-local JSON Pointer cannot be resolved."""
