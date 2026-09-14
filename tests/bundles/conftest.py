import json
from io import StringIO
from pathlib import Path

import pytest

from ga4gh.gkm import bundles


def permissive_bundle_schema() -> StringIO:
    """Return a fresh schema for tests that do not exercise schema rules."""
    return StringIO(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
            }
        )
    )


@pytest.fixture(autouse=True)
def provide_schema_for_bundle_tests(monkeypatch):
    """Supply an explicit permissive schema to bundle test calls."""
    original_load_bundle = bundles.load_bundle

    def load_bundle(source, *, schema=None, serialization=None):
        """Load a bundle with a permissive schema when none is supplied."""
        if schema is None:
            schema = permissive_bundle_schema()
        return original_load_bundle(
            source,
            schema=schema,
            serialization=serialization,
        )

    monkeypatch.setattr(bundles, "load_bundle", load_bundle)
    return original_load_bundle


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
