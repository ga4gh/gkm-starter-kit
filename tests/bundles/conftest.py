from pathlib import Path

import pytest

from ga4gh.gkm import bundles

SEQUENCE_ID = "SQ.6CnHhDq_bDCsuIBf0AzxtKq_lXYM7f0m"
BUNDLE_DIR = Path(__file__).parents[2] / "notebooks" / "civic" / "bundles"


@pytest.fixture(autouse=True)
def register_example_bundles():
    """Register the notebook fixtures used by named-source tests."""
    for assertion_id in ("9", "251"):
        bundles.registry.register(
            bundles.BundleRegistration(
                name=f"civic-assertion-{assertion_id}",
                source=BUNDLE_DIR / f"civic-assertion-{assertion_id}-bundle.json",
                schema=BUNDLE_DIR / "civic-gks-bundle-v0.1.0.schema.json",
                producer="CIViC",
            ),
            replace=True,
        )
