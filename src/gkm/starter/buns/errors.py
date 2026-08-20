"""Exceptions raised by the bun API."""


class BunError(Exception):
    """Base class for bun-related errors."""


class BunNotFoundError(BunError):
    """Raised when a bun source cannot be found."""


class BunFormatError(BunError):
    """Raised when a bun's serialization or document format is unsupported."""


class BunCompatibilityError(BunFormatError):
    """Raised when a bun schema is incompatible with installed GKM models."""


class BunReferenceError(BunError):
    """Raised when a bun-local JSON Pointer cannot be resolved."""
