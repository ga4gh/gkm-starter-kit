"""Genomic Knowledge Model Starter Kit."""

from importlib.metadata import PackageNotFoundError, version

from . import bundles
from .bundles import (
    Bundle,
    BundleCollection,
    check_gkm_version_compatibility,
    load_bundle,
    load_bundles,
    supported_gkm_versions,
)

try:
    __version__ = version("gkm.starter")
except PackageNotFoundError:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

__all__ = [
    "Bundle",
    "BundleCollection",
    "bundles",
    "check_gkm_version_compatibility",
    "load_bundle",
    "load_bundles",
    "supported_gkm_versions",
]
