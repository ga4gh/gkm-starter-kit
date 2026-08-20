"""Exceptions raised by the bundle API."""


class BundleError(Exception):
    """Base class for bundle-related errors."""


class BundleNotFoundError(BundleError):
    """Raised when a bundle source cannot be found."""


class BundleFormatError(BundleError):
    """Raised when a bundle's serialization or document format is unsupported."""


class BundleCompatibilityError(BundleFormatError):
    """Raised when a bundle schema is incompatible with installed GKM models."""


class BundleReferenceError(BundleError):
    """Raised when a bundle-local JSON Pointer cannot be resolved."""
