"""Genomic Knowledge Model Starter Kit."""

from importlib.metadata import PackageNotFoundError, version

from . import buns
from .buns import (
    Bun,
    BunCollection,
    check_gkm_version_compatibility,
    load_bun,
    load_buns,
    supported_gkm_versions,
)

try:
    __version__ = version("gkm.starter")
except PackageNotFoundError:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

__all__ = [
    "Bun",
    "BunCollection",
    "buns",
    "check_gkm_version_compatibility",
    "load_bun",
    "load_buns",
    "supported_gkm_versions",
]
