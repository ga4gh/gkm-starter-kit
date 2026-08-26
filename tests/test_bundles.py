import json
from io import StringIO
from pathlib import Path

import pytest
from ga4gh.vrs.models import SequenceReference

from ga4gh.gkm import bundles
from ga4gh.gkm.bundles import (
    BundleCompatibilityError,
    BundleConflictError,
    BundleNotFoundError,
    BundleReferenceError,
    BundleSerializationError,
    BundleValidationError,
)

SEQUENCE_ID = "SQ.6CnHhDq_bDCsuIBf0AzxtKq_lXYM7f0m"
BUNDLE_DIR = Path(__file__).parents[1] / "notebooks" / "civic" / "bundles"


@pytest.fixture(autouse=True)
def register_example_bundles():
    """Register the notebook fixtures used by named-source tests."""
    for assertion_id in ("9", "251"):
        bundles.registry.register(
            bundles.BundleRegistration(
                name=f"civic-aid-{assertion_id}",
                source=BUNDLE_DIR / f"civic-aid-{assertion_id}-bundle.json",
                schema=BUNDLE_DIR / "civic-gks-bundle-v0.1.0.schema.json",
                producer="CIViC",
            ),
            replace=True,
        )


def test_supported_gkm_versions():
    versions = bundles.supported_gkm_versions()

    assert set(versions) == {"gks-core", "vrs", "cat-vrs", "va-spec"}
    assert all(versions.values())


def test_check_gkm_version_compatibility_is_public():
    schema = {
        "$ref": f"https://w3id.org/ga4gh/schema/vrs/{bundles.supported_gkm_versions()['vrs']}/json/Allele"
    }

    bundles.check_gkm_version_compatibility(schema)
    bundles.check_gkm_version_compatibility(schema)


def test_load_registered_civic_bundle():
    civic = bundles.load_bundle("civic-aid-9")

    sequence_reference = civic.sequenceReference[SEQUENCE_ID]

    assert isinstance(civic, bundles.Bundle)
    assert isinstance(sequence_reference, SequenceReference)
    assert sequence_reference.refgetAccession == SEQUENCE_ID


def test_collection_names():
    civic = bundles.load_bundle("civic-aid-9")

    assert civic.collection_names() == tuple(civic.keys())
    assert civic.collection_names()[0] == "sequenceReference"
    assert "assertion" in civic.collection_names()
    assert SEQUENCE_ID in list(civic.sequenceReference.keys())


def test_bundle_and_collection_protocols():
    civic = bundles.load_bundle("civic-aid-9")
    sequence_references = civic.sequenceReference

    assert len(civic) == 17
    assert repr(civic) == "Bundle(name='civic-aid-9', collections=17)"
    assert civic.collection("sequenceReference") is sequence_references
    assert len(sequence_references) == 3
    assert repr(sequence_references) == (
        "BundleCollection(name='sequenceReference', size=3)"
    )


def test_missing_collection_raises_contextual_bundle_error():
    civic = bundles.load_bundle("civic-aid-9")

    with pytest.raises(
        bundles.BundleCollectionNotFoundError,
        match="Unknown collection 'sequenceReferences'",
    ) as error:
        civic.sequenceReferences  # noqa: B018

    assert isinstance(error.value, bundles.BundleError)
    assert isinstance(error.value, AttributeError)
    assert isinstance(error.value, KeyError)


def test_missing_collection_object_raises_contextual_bundle_error():
    civic = bundles.load_bundle("civic-aid-9")

    with pytest.raises(
        bundles.BundleObjectNotFoundError,
        match=r"Unknown identifier 'SQ[.]not-found' in collection 'sequenceReference'",
    ) as error:
        civic.sequenceReference["SQ.not-found"]

    assert isinstance(error.value, bundles.BundleError)
    assert isinstance(error.value, KeyError)


def test_resolve_reference():
    civic = bundles.load_bundle("civic-aid-9")

    resolved = civic.resolve(f"#/sequenceReference/{SEQUENCE_ID}")

    assert resolved is civic.sequenceReference[SEQUENCE_ID]


def test_resolve_traverses_models_and_lists():
    civic = bundles.load_bundle("civic-aid-9")

    assert (
        civic.resolve(f"#/sequenceReference/{SEQUENCE_ID}/refgetAccession")
        == SEQUENCE_ID
    )
    assert (
        civic.resolve(
            "#/assertion/civic.aid:9/hasEvidenceLines/0/directionOfEvidenceProvided"
        )
        == "supports"
    )


def test_dereference():
    civic = bundles.load_bundle("civic-aid-251")

    inline = civic.dereference()

    assertion = inline["assertion"]["civic.aid:251"]
    assert assertion["proposition"]["type"] == "VariantOncogenicityProposition"
    cycle = inline["molecularProfile"]["civic.mpid:82"]["mappings"][0]["coding"]
    assert cycle["mappings"][0]["coding"] == "#/molecularProfile/civic.mpid:82"
    assert civic.to_dict()["assertion"]["civic.aid:251"]["proposition"].startswith("#/")


def test_dereference_from_value():
    civic = bundles.load_bundle("civic-aid-9")
    proposition = civic.resolve(civic.assertion["civic.aid:9"]["proposition"])

    inline = civic.dereference(proposition)

    assert inline["type"] == "VariantClinicalSignificanceProposition"
    assert isinstance(inline["subjectVariant"], dict)


def test_resolve_bad_reference():
    civic = bundles.load_bundle("civic-aid-9")

    with pytest.raises(BundleReferenceError):
        civic.resolve("#/sequenceReference/missing")


def test_resolve_rejects_nonlocal_reference():
    civic = bundles.load_bundle("civic-aid-9")

    with pytest.raises(BundleReferenceError, match="Expected a bundle-local"):
        civic.resolve("https://example.org/object")


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

    bundle = bundles.load_bundle(stream)

    assert isinstance(bundle.sequenceReference[SEQUENCE_ID], SequenceReference)


def test_reference_model_validation_error_is_translated():
    stream = StringIO(
        json.dumps(
            {
                "sequenceReference": {
                    "invalid": {"type": "SequenceReference"},
                }
            }
        )
    )

    with pytest.raises(
        BundleValidationError,
        match="Invalid 'SequenceReference' bundle object",
    ) as error:
        bundles.load_bundle(stream)

    assert error.value.__cause__.__class__.__name__ == "ValidationError"


def test_reference_does_not_hide_unrelated_validation_error():
    stream = StringIO(
        json.dumps(
            {
                "sequenceReference": {
                    "invalid": {
                        "type": "SequenceReference",
                        "related": "#/objects/related",
                    },
                }
            }
        )
    )

    with pytest.raises(BundleValidationError):
        bundles.load_bundle(stream)


def test_reject_incompatible_gkm_schema_version():
    bundle = StringIO(json.dumps({"objects": {}}))
    schema = StringIO(
        json.dumps({"$ref": "https://w3id.org/ga4gh/schema/vrs/0.0.0/json/Allele"})
    )

    with pytest.raises(BundleCompatibilityError, match=r"vrs references '0.0.0'"):
        bundles.load_bundle(bundle, schema=schema)


@pytest.mark.parametrize("value", ["not JSON", "[1, 2, 3]"])
def test_reject_invalid_bundle_serialization(value):
    with pytest.raises(BundleSerializationError):
        bundles.load_bundle(StringIO(value))


def test_reject_invalid_schema_shape():
    bundle = StringIO(json.dumps({"objects": {}}))
    schema = StringIO(json.dumps([]))

    with pytest.raises(BundleSerializationError, match="schema must be a JSON object"):
        bundles.load_bundle(bundle, schema=schema)


def test_reject_invalid_metadata_shape():
    bundle = StringIO(json.dumps({"objects": {}, "metadata": []}))

    with pytest.raises(
        BundleSerializationError,
        match="metadata must be a JSON object",
    ):
        bundles.load_bundle(bundle)


def test_reject_registered_bundle_with_missing_source(tmp_path):
    bundles.registry.register(
        bundles.BundleRegistration(
            name="missing-bundle",
            source=tmp_path / "missing.json",
        ),
        replace=True,
    )

    with pytest.raises(BundleNotFoundError, match=r"missing\.json"):
        bundles.load_bundle("missing-bundle")


def test_reject_missing_bundle_path(tmp_path):
    with pytest.raises(BundleNotFoundError, match=r"missing[.]json"):
        bundles.load_bundle(tmp_path / "missing.json")


def test_load_bundles():
    loaded = bundles.load_bundles("civic-aid-9", "civic-aid-251")

    assert set(loaded) == {"civic-aid-9", "civic-aid-251"}


def test_load_bundles_rejects_duplicate_names():
    source = BUNDLE_DIR / "civic-aid-9-bundle.json"

    with pytest.raises(
        BundleConflictError,
        match="Multiple bundles resolved to the name",
    ):
        bundles.load_bundles(source, source)


def test_write_round_trip(tmp_path):
    civic = bundles.load_bundle("civic-aid-9")
    destination = tmp_path / "round-trip.json"

    civic.write(destination)
    reloaded = bundles.load_bundle(destination)

    assert reloaded.to_dict() == civic.to_dict()


def test_write_serializes_metadata(tmp_path):
    civic = bundles.load_bundle("civic-aid-9")
    destination = tmp_path / "baked.json"

    civic.write(destination)

    assert json.loads(destination.read_text())["metadata"] == civic.metadata


def test_reject_unsupported_write_serialization(tmp_path):
    civic = bundles.load_bundle("civic-aid-9")

    with pytest.raises(BundleSerializationError, match="Unsupported serialization"):
        civic.write(tmp_path / "bundle.json", serialization="jsonl")


def test_write_translates_json_encoding_error(tmp_path):
    civic = bundles.load_bundle("civic-aid-9")
    civic.metadata["invalid"] = object()

    with pytest.raises(
        BundleSerializationError,
        match="cannot be serialized as JSON",
    ) as error:
        civic.write(tmp_path / "bundle.json")

    assert isinstance(error.value.__cause__, TypeError)


def test_reject_unsupported_serialization():
    with pytest.raises(BundleSerializationError):
        bundles.load_bundle("civic", serialization="parquet")


def test_bundles_namespace():
    assert isinstance(bundles.registry, bundles.BundleRegistry)
    assert "civic-aid-9" in bundles.registry.registered_names()
    assert bundles.registry.get_registration("civic-aid-9").producer == "CIViC"


def test_registry_rejects_duplicate_name():
    registration = bundles.registry.get_registration("civic-aid-9")

    with pytest.raises(BundleConflictError, match="already registered"):
        bundles.registry.register(registration)


def test_registry_rejects_unknown_name():
    with pytest.raises(BundleNotFoundError, match="Unknown bundle 'missing'"):
        bundles.registry.get_registration("missing")
