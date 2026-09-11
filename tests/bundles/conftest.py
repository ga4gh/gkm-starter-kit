from pathlib import Path

import pytest

from ga4gh.gkm import bundles


@pytest.fixture
def sequence_id() -> str:
    return "SQ.6CnHhDq_bDCsuIBf0AzxtKq_lXYM7f0m"


@pytest.fixture
def bundle_dir() -> Path:
    return Path(__file__).parents[2] / "notebooks" / "civic" / "bundles"


@pytest.fixture
def sequence_reference_bundle(sequence_id) -> dict:
    return {
        "sequenceReference": {
            sequence_id: {
                "type": "SequenceReference",
                "refgetAccession": sequence_id,
            }
        },
        "metadata": {"bundleFormat": "example-bundle"},
    }


@pytest.fixture(autouse=True)
def register_example_bundles(bundle_dir):
    """Register the notebook fixtures used by named-source tests."""
    for assertion_id in ("9", "251"):
        bundles.registry.register(
            bundles.BundleRegistration(
                name=f"civic-assertion-{assertion_id}",
                source=bundle_dir / f"civic-assertion-{assertion_id}-bundle.json",
                schema=bundle_dir / "civic-gks-bundle-v0.1.0.schema.json",
                producer="CIViC",
            ),
            replace=True,
        )
