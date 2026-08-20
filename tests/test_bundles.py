import json
from io import StringIO
from pathlib import Path

import pytest
from ga4gh.vrs.models import SequenceReference

from gkm import starter
from gkm.starter.bundles import (
    BundleCompatibilityError,
    BundleFormatError,
    BundleNotFoundError,
    BundleReferenceError,
)

SEQUENCE_ID = "SQ.6CnHhDq_bDCsuIBf0AzxtKq_lXYM7f0m"
BUNDLE_DIR = Path(__file__).parents[1] / "notebooks" / "civic" / "bundles"


@pytest.fixture(autouse=True)
def register_example_bundles():
    """Register the notebook fixtures used by named-source tests."""
    for assertion_id in ("9", "251"):
        starter.bundles.register(
            starter.bundles.BundleRegistration(
                name=f"civic-aid-{assertion_id}",
                source=BUNDLE_DIR / f"civic-aid-{assertion_id}-bundle.json",
                schema=BUNDLE_DIR / "civic-gks-bundle-v0.1.0.schema.json",
                producer="CIViC",
            ),
            replace=True,
        )


def test_supported_gkm_versions():
    versions = starter.supported_gkm_versions()

    assert set(versions) == {"gks-core", "vrs", "cat-vrs", "va-spec"}
    assert all(versions.values())


def test_check_gkm_version_compatibility_is_public():
    schema = {
        "$ref": f"https://w3id.org/ga4gh/schema/vrs/{starter.supported_gkm_versions()['vrs']}/json/Allele"
    }

    starter.check_gkm_version_compatibility(schema)
    starter.bundles.check_gkm_version_compatibility(schema)


def test_load_registered_civic_bundle():
    civic = starter.load_bundle("civic-aid-9")

    sequence_reference = civic.sequenceReference[SEQUENCE_ID]

    assert isinstance(civic, starter.Bundle)
    assert isinstance(sequence_reference, SequenceReference)
    assert sequence_reference.refgetAccession == SEQUENCE_ID


def test_collection_names():
    civic = starter.load_bundle("civic-aid-9")

    assert civic.collection_names() == tuple(civic.keys())
    assert civic.collection_names()[0] == "sequenceReference"
    assert "assertion" in civic.collection_names()


def test_resolve_reference():
    civic = starter.load_bundle("civic-aid-9")

    resolved = civic.resolve(f"#/sequenceReference/{SEQUENCE_ID}")

    assert resolved is civic.sequenceReference[SEQUENCE_ID]


def test_dereference_reference():
    civic = starter.load_bundle("civic-aid-9")

    resolved = civic.resolve(f"#/sequenceReference/{SEQUENCE_ID}")

    assert resolved is civic.sequenceReference[SEQUENCE_ID]


def test_dereference():
    civic = starter.load_bundle("civic-aid-251")

    inline = civic.dereference()

    assertion = inline["assertion"]["civic.aid:251"]
    assert assertion["proposition"]["type"] == "VariantOncogenicityProposition"
    cycle = inline["molecularProfile"]["civic.mpid:82"]["mappings"][0]["coding"]
    assert cycle["mappings"][0]["coding"] == "#/molecularProfile/civic.mpid:82"
    assert civic.to_dict()["assertion"]["civic.aid:251"]["proposition"].startswith("#/")


def test_dereference_from_value():
    civic = starter.load_bundle("civic-aid-9")
    proposition = civic.resolve(civic.assertion["civic.aid:9"]["proposition"])

    inline = civic.dereference(proposition)

    assert inline["type"] == "VariantClinicalSignificanceProposition"
    assert isinstance(inline["subjectVariant"], dict)


def test_dereference_is_plain_alias():
    civic = starter.load_bundle("civic-aid-251")

    assert civic.dereference() == civic.dereference()


def test_resolve_bad_reference():
    civic = starter.load_bundle("civic-aid-9")

    with pytest.raises(BundleReferenceError):
        civic.resolve("#/sequenceReference/missing")


def test_load_json_stream():
    stream = StringIO(
        json.dumps(
            {
                "sequenceReference": {
                    SEQUENCE_ID: {
                        "type": "SequenceReference",
                        "refgetAccession": SEQUENCE_ID,
                    }
                },
                "metadata": {"bundleFormat": "example-bundle"},
            }
        )
    )

    bundle = starter.load_bundle(stream)

    assert isinstance(bundle.sequenceReference[SEQUENCE_ID], SequenceReference)


def test_reject_incompatible_gkm_schema_version():
    bundle = StringIO(json.dumps({"objects": {}}))
    schema = StringIO(
        json.dumps({"$ref": "https://w3id.org/ga4gh/schema/vrs/0.0.0/json/Allele"})
    )

    with pytest.raises(BundleCompatibilityError, match=r"vrs references '0.0.0'"):
        starter.load_bundle(bundle, schema=schema)


@pytest.mark.parametrize("value", ["not JSON", "[1, 2, 3]"])
def test_reject_invalid_bundle_document(value):
    with pytest.raises(BundleFormatError):
        starter.load_bundle(StringIO(value))


def test_reject_invalid_schema_shape():
    bundle = StringIO(json.dumps({"objects": {}}))
    schema = StringIO(json.dumps([]))

    with pytest.raises(BundleFormatError, match="schema must be a JSON object"):
        starter.load_bundle(bundle, schema=schema)


def test_reject_registered_bundle_with_missing_source(tmp_path):
    starter.bundles.register(
        starter.bundles.BundleRegistration(
            name="missing-bundle",
            source=tmp_path / "missing.json",
        ),
        replace=True,
    )

    with pytest.raises(BundleNotFoundError, match=r"missing\.json"):
        starter.load_bundle("missing-bundle")


def test_load_bundles():
    loaded = starter.load_bundles("civic-aid-9", "civic-aid-251")

    assert set(loaded) == {"civic-aid-9", "civic-aid-251"}


def test_write_round_trip(tmp_path):
    civic = starter.load_bundle("civic-aid-9")
    destination = tmp_path / "round-trip.json"

    civic.write(destination)
    reloaded = starter.load_bundle(destination)

    assert reloaded.to_dict() == civic.to_dict()


def test_bake_writes_json(tmp_path):
    civic = starter.load_bundle("civic-aid-9")
    destination = tmp_path / "baked.json"

    civic.write(destination)

    assert json.loads(destination.read_text())["metadata"] == civic.metadata


def test_reject_unsupported_serialization():
    with pytest.raises(BundleFormatError):
        starter.load_bundle("civic", serialization="parquet")


def test_bundles_namespace():
    assert isinstance(starter.bundles.registry, starter.bundles.BundleRegistry)
    assert "civic-aid-9" in starter.bundles.registered_names()
    assert starter.bundles.get_registration("civic-aid-9").producer == "CIViC"
