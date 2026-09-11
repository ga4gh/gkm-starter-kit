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
                name=f"civic-assertion-{assertion_id}",
                source=BUNDLE_DIR / f"civic-assertion-{assertion_id}-bundle.json",
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
    civic = bundles.load_bundle("civic-assertion-9")

    sequence_reference = civic.sequenceReference[SEQUENCE_ID]

    assert isinstance(civic, bundles.Bundle)
    assert isinstance(sequence_reference, SequenceReference)
    assert sequence_reference.refgetAccession == SEQUENCE_ID


def test_collection_names():
    civic = bundles.load_bundle("civic-assertion-9")

    assert civic.collection_names() == tuple(civic.keys())
    assert civic.collection_names()[0] == "sequenceReference"
    assert "assertion" in civic.collection_names()
    assert SEQUENCE_ID in list(civic.sequenceReference.keys())


def test_bundle_and_collection_protocols():
    civic = bundles.load_bundle("civic-assertion-9")
    sequence_references = civic.sequenceReference

    assert len(civic) == 17
    assert repr(civic) == "Bundle(name='civic-assertion-9', collections=17)"
    assert civic.collection("sequenceReference") is sequence_references
    assert len(sequence_references) == 3
    assert repr(sequence_references) == (
        "BundleCollection(name='sequenceReference', size=3)"
    )


def test_missing_collection_raises_contextual_bundle_error():
    civic = bundles.load_bundle("civic-assertion-9")

    with pytest.raises(
        bundles.BundleCollectionNotFoundError,
        match="Unknown collection 'sequenceReferences'",
    ) as error:
        civic.sequenceReferences  # noqa: B018

    assert isinstance(error.value, bundles.BundleError)
    assert isinstance(error.value, AttributeError)
    assert isinstance(error.value, KeyError)


def test_missing_collection_object_raises_contextual_bundle_error():
    civic = bundles.load_bundle("civic-assertion-9")

    with pytest.raises(
        bundles.BundleObjectNotFoundError,
        match=r"Unknown identifier 'SQ[.]not-found' in collection 'sequenceReference'",
    ) as error:
        civic.sequenceReference["SQ.not-found"]

    assert isinstance(error.value, bundles.BundleError)
    assert isinstance(error.value, KeyError)


def test_resolve_reference():
    civic = bundles.load_bundle("civic-assertion-9")

    resolved = civic.resolve(f"#/sequenceReference/{SEQUENCE_ID}")

    assert resolved is civic.sequenceReference[SEQUENCE_ID]


def test_resolve_traverses_models_and_lists():
    civic = bundles.load_bundle("civic-assertion-9")

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


def test_normalize():
    civic = bundles.load_bundle("civic-assertion-251")

    inline = civic.normalize()

    assertion = inline["assertion"]["civic.aid:251"]
    assert assertion["proposition"]["type"] == "VariantOncogenicityProposition"
    cycle = inline["molecularProfile"]["civic.mpid:82"]["mappings"][0]["coding"]
    assert cycle["mappings"][0]["coding"] == "#/molecularProfile/civic.mpid:82"
    assert civic.to_dict()["assertion"]["civic.aid:251"]["proposition"].startswith("#/")


def test_normalize_from_value():
    civic = bundles.load_bundle("civic-assertion-9")
    proposition = civic.resolve(civic.assertion["civic.aid:9"]["proposition"])

    inline = civic.normalize(proposition)

    assert inline["type"] == "VariantClinicalSignificanceProposition"
    assert isinstance(inline["subjectVariant"], dict)


def test_normalize_and_export_round_trip():
    civic = bundles.load_bundle("civic-assertion-9")
    original = civic.assertion["civic.aid:9"]

    normalized = civic.normalize(original)
    exported = civic.export(normalized)
    deep_exported = civic.export(original, deep=True)

    assert exported["proposition"] == original["proposition"]
    assert exported["id"] == "civic.aid:9"
    assert isinstance(deep_exported["proposition"], dict)


def test_denormalize_replaces_nested_objects_by_content_or_identity():
    """Denormalization uses generic bundle identity rules, not producer names."""
    civic = bundles.load_bundle("civic-assertion-9")
    sequence = civic.sequenceReference[SEQUENCE_ID].model_dump(
        mode="json", exclude_none=True
    )
    assertion = dict(civic.assertion["civic.aid:9"])
    normalized = {
        "sequence": sequence,
        "updated_assertion": {**assertion, "description": "updated"},
        "producer_object": {"id": "producer-1", "type": "OtherObject"},
    }

    exported = civic.denormalize(normalized)

    assert exported["sequence"] == f"#/sequenceReference/{SEQUENCE_ID}"
    assert exported["updated_assertion"] == "#/assertion/civic.aid:9"
    assert exported["producer_object"] == normalized["producer_object"]


def test_export_shallow_preserves_bundle_and_deep_normalizes_it():
    civic = bundles.load_bundle("civic-assertion-9")

    shallow = civic.export()
    deep = civic.export(deep=True)

    assert shallow["assertion"]["civic.aid:9"]["proposition"].startswith("#/")
    assert isinstance(deep["assertion"]["civic.aid:9"]["proposition"], dict)


def test_export_rejects_non_json_content():
    civic = bundles.load_bundle("civic-assertion-9")

    with pytest.raises(
        bundles.BundleSerializationError, match="cannot be denormalized"
    ):
        civic.export({"invalid": object()})


def test_export_rejects_invalid_result(monkeypatch):
    """Export validates results even if an internal conversion returns bad data."""
    civic = bundles.load_bundle("civic-assertion-9")
    monkeypatch.setattr(civic, "denormalize", lambda value: {"invalid": object()})  # noqa: ARG005

    with pytest.raises(
        bundles.BundleSerializationError, match="Exported content is not valid JSON"
    ):
        civic.export({"valid": True})


def test_to_dict_includes_metadata_and_producer_extras():
    """Serialization retains top-level metadata and producer-defined extras."""
    bundle = bundles.Bundle(
        {},
        metadata={"bundleFormat": "example"},
        extras={"producerExtension": {"enabled": True}},
    )

    assert bundle.to_dict() == {
        "metadata": {"bundleFormat": "example"},
        "producerExtension": {"enabled": True},
    }

    without_metadata = bundles.Bundle({}, extras={"producerExtension": {}})
    assert without_metadata.to_dict() == {"producerExtension": {}}


def test_resolve_bad_reference():
    civic = bundles.load_bundle("civic-assertion-9")

    with pytest.raises(BundleReferenceError):
        civic.resolve("#/sequenceReference/missing")


def test_resolve_rejects_nonlocal_reference():
    civic = bundles.load_bundle("civic-assertion-9")

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


def test_load_validates_all_bundle_references():
    stream = StringIO(
        json.dumps(
            {
                "objects": {
                    "first": {"related": "#/objects/second"},
                    "second": {"value": "ok"},
                },
                "metadata": {"related": "#/objects/first"},
                "producerExtension": [{"related": "#/objects/second"}],
            }
        )
    )

    bundle = bundles.load_bundle(stream)

    assert bundle.extras["producerExtension"][0]["related"] == "#/objects/second"


def test_load_reports_all_invalid_bundle_references():
    stream = StringIO(
        json.dumps(
            {
                "objects": {
                    "first": {"related": "#/objects/missing"},
                    "second": {"related": "#/unknown"},
                },
                "metadata": {"related": "#/objects/first/missing"},
            }
        )
    )

    with pytest.raises(BundleReferenceError) as error:
        bundles.load_bundle(stream)

    message = str(error.value)
    assert "3 total" in message
    assert "#/objects/missing" in message
    assert "#/unknown" in message
    assert "#/objects/first/missing" in message


def test_load_bounds_many_invalid_reference_details():
    stream = StringIO(
        json.dumps({"objects": [f"#/missing/{index}" for index in range(60)]})
    )

    with pytest.raises(BundleReferenceError, match="60 total") as error:
        bundles.load_bundle(stream)

    assert "additional failure(s)" in str(error.value)


def test_load_reports_invalid_pointer_traversal():
    stream = StringIO(json.dumps({"objects": [1], "related": "#/objects/0/value"}))

    with pytest.raises(BundleReferenceError, match="cannot traverse scalar value"):
        bundles.load_bundle(stream)


@pytest.mark.parametrize(
    ("pointer", "message"),
    [
        ("#/objects/-1", "invalid JSON Pointer array index"),
        ("#/objects/01", "invalid JSON Pointer array index"),
        ("#/objects/9", "out of bounds"),
        ("#/objects/~2", "invalid JSON Pointer escape"),
    ],
)
def test_load_reports_invalid_json_pointer_syntax(pointer, message):
    stream = StringIO(json.dumps({"objects": ["value"], "related": pointer}))

    with pytest.raises(BundleReferenceError, match=message):
        bundles.load_bundle(stream)


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
                        "related": "#/sequenceReference/invalid",
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
    loaded = bundles.load_bundles("civic-assertion-9", "civic-assertion-251")

    assert set(loaded) == {"civic-assertion-9", "civic-assertion-251"}


def test_load_bundles_rejects_duplicate_names():
    source = BUNDLE_DIR / "civic-assertion-9-bundle.json"

    with pytest.raises(
        BundleConflictError,
        match="Multiple bundles resolved to the name",
    ):
        bundles.load_bundles(source, source)


def test_write_round_trip(tmp_path):
    civic = bundles.load_bundle("civic-assertion-9")
    destination = tmp_path / "round-trip.json"

    civic.write(destination)
    reloaded = bundles.load_bundle(destination)

    assert reloaded.to_dict() == civic.to_dict()


def test_write_serializes_metadata(tmp_path):
    civic = bundles.load_bundle("civic-assertion-9")
    destination = tmp_path / "baked.json"

    civic.write(destination)

    assert json.loads(destination.read_text())["metadata"] == civic.metadata


def test_reject_unsupported_write_serialization(tmp_path):
    civic = bundles.load_bundle("civic-assertion-9")

    with pytest.raises(BundleSerializationError, match="Unsupported serialization"):
        civic.write(tmp_path / "bundle.json", serialization="jsonl")


def test_write_translates_json_encoding_error(tmp_path):
    civic = bundles.load_bundle("civic-assertion-9")
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
    assert "civic-assertion-9" in bundles.registry.registered_names()
    assert bundles.registry.get_registration("civic-assertion-9").producer == "CIViC"


def test_registry_rejects_duplicate_name():
    registration = bundles.registry.get_registration("civic-assertion-9")

    with pytest.raises(BundleConflictError, match="already registered"):
        bundles.registry.register(registration)


def test_registry_rejects_unknown_name():
    with pytest.raises(BundleNotFoundError, match="Unknown bundle 'missing'"):
        bundles.registry.get_registration("missing")
