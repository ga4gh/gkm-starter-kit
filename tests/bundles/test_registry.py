from pathlib import Path

import pytest

from ga4gh.gkm import bundles
from ga4gh.gkm.bundles import (
    BundleConflictError,
    BundleNotFoundError,
)

SEQUENCE_ID = "SQ.6CnHhDq_bDCsuIBf0AzxtKq_lXYM7f0m"
BUNDLE_DIR = Path(__file__).parents[2] / "notebooks" / "civic" / "bundles"


def test_bundles_namespace():
    assert isinstance(bundles.registry, bundles.BundleRegistry)
    assert "civic-assertion-9" in bundles.registry.registered_names()
    assert bundles.registry.get_registration("civic-assertion-9").producer == "CIViC"


def test_registry_rejects_duplicate_name():
    registration = bundles.registry.get_registration("civic-assertion-9")

    with pytest.raises(BundleConflictError, match="already registered"):
        bundles.registry.register(registration)


def test_registry_rejects_unknown_name():
    with pytest.raises(BundleNotFoundError, match="Unknown bundle 'missing'"):
        bundles.registry.get_registration("missing")
