"""Compatibility checks for GKM product schemas."""

# ruff: noqa: ANN401

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from ga4gh.cat_vrs import CATVRS_VERSION
from ga4gh.core import CORE_VERSION
from ga4gh.va_spec import VASPEC_VERSION
from ga4gh.vrs import VRS_VERSION

from .errors import BundleCompatibilityError

_W3ID_SCHEMA_REFERENCE = re.compile(
    r"^https://w3id\.org/ga4gh/schema/"
    r"(?P<product>gks-core|vrs|cat-vrs|va-spec)/(?P<version>[^/]+)/"
)
_SUPPORTED_VERSIONS = {
    "gks-core": CORE_VERSION,
    "vrs": VRS_VERSION,
    "cat-vrs": CATVRS_VERSION,
    "va-spec": VASPEC_VERSION,
}


def supported_gkm_versions() -> dict[str, str]:
    """Return the latest GKM product versions supported by this installation.

    :return: Product names mapped to their supported schema versions.
    """
    return dict(_SUPPORTED_VERSIONS)


def _references(value: Any) -> list[str]:
    """Collect JSON Schema references recursively.

    :param value: JSON-compatible schema value to inspect.
    :return: Every string-valued ``$ref`` in the value.
    """
    if isinstance(value, Mapping):
        found = [value["$ref"]] if isinstance(value.get("$ref"), str) else []

        for item in value.values():
            found.extend(_references(item))

        return found

    if isinstance(value, list):
        found = []

        for item in value:
            found.extend(_references(item))

        return found

    return []


def check_gkm_version_compatibility(schema: Mapping[str, Any]) -> None:
    """Check GKM W3ID references against installed product versions.

    Each recognized reference must exactly match the version reported by
    :func:`supported_gkm_versions`.

    References outside the versioned GA4GH W3ID schema namespace are ignored.

    :param schema: Producer JSON Schema to inspect.
    :raises BundleCompatibilityError: If a GKM schema version does not match the
        installed reference implementation.
    """
    mismatches: set[tuple[str, str, str]] = set()
    for reference in _references(schema):
        match = _W3ID_SCHEMA_REFERENCE.match(reference)
        if match is None:
            continue

        product = match.group("product")
        referenced = match.group("version")
        supported = _SUPPORTED_VERSIONS[product]

        if referenced != supported:
            mismatches.add((product, referenced, supported))

    if mismatches:
        details = "; ".join(
            f"{product} references {referenced!r}, but the installed "
            f"implementation supports {supported!r}"
            for product, referenced, supported in sorted(mismatches)
        )
        message = f"Incompatible GKM schema versions: {details}"
        raise BundleCompatibilityError(message)
