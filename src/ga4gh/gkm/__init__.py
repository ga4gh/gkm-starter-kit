"""Python tools for the GA4GH Genomic Knowledge Model."""

from importlib.metadata import PackageNotFoundError, version

from ga4gh.gkm import bundles

try:
    __version__ = version("ga4gh.gkm")
except PackageNotFoundError:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

__all__ = ["bundles"]
