import json
from io import StringIO
from pathlib import Path

import pytest
from ga4gh.vrs.models import SequenceReference

from gkm import starter
from gkm.starter.buns import (
    BunCompatibilityError,
    BunFormatError,
    BunNotFoundError,
    BunReferenceError,
)

SEQUENCE_ID = "SQ.6CnHhDq_bDCsuIBf0AzxtKq_lXYM7f0m"
BUNDLE_DIR = Path(__file__).parents[1] / "notebooks" / "civic" / "bundles"


@pytest.fixture(autouse=True)
def register_example_buns():
    """Register the notebook fixtures used by named-source tests."""
    for assertion_id in ("9", "251"):
        starter.buns.register(
            starter.buns.BunRegistration(
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
    starter.buns.check_gkm_version_compatibility(schema)


def test_load_registered_civic_bun():
    civic = starter.load_bun("civic-aid-9")

    sequence_reference = civic.sequenceReference[SEQUENCE_ID]

    assert isinstance(civic, starter.Bun)
    assert isinstance(sequence_reference, SequenceReference)
    assert sequence_reference.refgetAccession == SEQUENCE_ID


def test_collection_names():
    civic = starter.load_bun("civic-aid-9")

    assert civic.collection_names() == tuple(civic.keys())
    assert civic.collection_names()[0] == "sequenceReference"
    assert "assertion" in civic.collection_names()


def test_resolve_reference():
    civic = starter.load_bun("civic-aid-9")

    resolved = civic.resolve(f"#/sequenceReference/{SEQUENCE_ID}")

    assert resolved is civic.sequenceReference[SEQUENCE_ID]


def test_unwrap_reference():
    civic = starter.load_bun("civic-aid-9")

    unwrapped = civic.unwrap(f"#/sequenceReference/{SEQUENCE_ID}")

    assert unwrapped is civic.sequenceReference[SEQUENCE_ID]


def test_unwrap_all():
    civic = starter.load_bun("civic-aid-251")

    inline = civic.unwrap_all()

    assertion = inline["assertion"]["civic.aid:251"]
    assert assertion["proposition"]["type"] == "VariantOncogenicityProposition"
    cycle = inline["molecularProfile"]["civic.mpid:82"]["mappings"][0]["coding"]
    assert cycle["mappings"][0]["coding"] == "#/molecularProfile/civic.mpid:82"
    assert civic.to_dict()["assertion"]["civic.aid:251"]["proposition"].startswith("#/")


def test_unwrap_all_from_value():
    civic = starter.load_bun("civic-aid-9")
    proposition = civic.unwrap(civic.assertion["civic.aid:9"]["proposition"])

    inline = civic.unwrap_all(proposition)

    assert inline["type"] == "VariantClinicalSignificanceProposition"
    assert isinstance(inline["subjectVariant"], dict)


def test_dereference_is_plain_alias():
    civic = starter.load_bun("civic-aid-251")

    assert civic.dereference() == civic.unwrap_all()


def test_resolve_bad_reference():
    civic = starter.load_bun("civic-aid-9")

    with pytest.raises(BunReferenceError):
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
                "metadata": {"bundleFormat": "example-bun"},
            }
        )
    )

    bun = starter.load_bun(stream)

    assert isinstance(bun.sequenceReference[SEQUENCE_ID], SequenceReference)


def test_reject_incompatible_gkm_schema_version():
    bun = StringIO(json.dumps({"objects": {}}))
    schema = StringIO(
        json.dumps({"$ref": "https://w3id.org/ga4gh/schema/vrs/0.0.0/json/Allele"})
    )

    with pytest.raises(BunCompatibilityError, match=r"vrs references '0.0.0'"):
        starter.load_bun(bun, schema=schema)


@pytest.mark.parametrize("value", ["not JSON", "[1, 2, 3]"])
def test_reject_invalid_bun_document(value):
    with pytest.raises(BunFormatError):
        starter.load_bun(StringIO(value))


def test_reject_invalid_schema_shape():
    bun = StringIO(json.dumps({"objects": {}}))
    schema = StringIO(json.dumps([]))

    with pytest.raises(BunFormatError, match="schema must be a JSON object"):
        starter.load_bun(bun, schema=schema)


def test_reject_registered_bun_with_missing_source(tmp_path):
    starter.buns.register(
        starter.buns.BunRegistration(
            name="missing-bun",
            source=tmp_path / "missing.json",
        ),
        replace=True,
    )

    with pytest.raises(BunNotFoundError, match=r"missing\.json"):
        starter.load_bun("missing-bun")


def test_load_buns():
    loaded = starter.load_buns("civic-aid-9", "civic-aid-251")

    assert set(loaded) == {"civic-aid-9", "civic-aid-251"}


def test_write_round_trip(tmp_path):
    civic = starter.load_bun("civic-aid-9")
    destination = tmp_path / "round-trip.json"

    civic.write(destination)
    reloaded = starter.load_bun(destination)

    assert reloaded.to_dict() == civic.to_dict()


def test_bake_writes_json(tmp_path):
    civic = starter.load_bun("civic-aid-9")
    destination = tmp_path / "baked.json"

    civic.bake(destination)

    assert json.loads(destination.read_text())["metadata"] == civic.metadata


def test_reject_unsupported_serialization():
    with pytest.raises(BunFormatError):
        starter.load_bun("civic", serialization="parquet")


def test_buns_namespace():
    assert isinstance(starter.buns.catalog, starter.buns.BunCatalog)
    assert "civic-aid-9" in starter.buns.registered_names()
    assert starter.buns.get_registration("civic-aid-9").producer == "CIViC"
