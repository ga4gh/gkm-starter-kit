import json
from io import StringIO
from pathlib import Path

import pytest

from ga4gh.gkm import bundles
from ga4gh.gkm.bundles import (
    BundleCompatibilityError,
)

SEQUENCE_ID = "SQ.6CnHhDq_bDCsuIBf0AzxtKq_lXYM7f0m"
BUNDLE_DIR = Path(__file__).parents[2] / "notebooks" / "civic" / "bundles"


def test_supported_gkm_versions():
    versions = bundles.supported_gkm_versions()

    assert set(versions) == {"gks-core", "vrs", "cat-vrs", "va-spec"}
    assert all(versions.values())


def test_reject_incompatible_gkm_schema_version():
    bundle = StringIO(json.dumps({"objects": {}}))
    schema = StringIO(
        json.dumps({"$ref": "https://w3id.org/ga4gh/schema/vrs/0.0.0/json/Allele"})
    )

    with pytest.raises(BundleCompatibilityError, match=r"vrs references '0.0.0'"):
        bundles.load_bundle(bundle, schema=schema)
