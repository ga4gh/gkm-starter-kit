import json
from io import StringIO
from pathlib import Path

import pytest

from ga4gh.gkm import bundles
from ga4gh.gkm.bundles import (
    BundleReferenceError,
    BundleValidationError,
)

SEQUENCE_ID = "SQ.6CnHhDq_bDCsuIBf0AzxtKq_lXYM7f0m"
BUNDLE_DIR = Path(__file__).parents[2] / "notebooks" / "civic" / "bundles"


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


def test_resolve_bad_reference():
    civic = bundles.load_bundle("civic-assertion-9")

    with pytest.raises(BundleReferenceError):
        civic.resolve("#/sequenceReference/missing")


def test_resolve_rejects_nonlocal_reference():
    civic = bundles.load_bundle("civic-assertion-9")

    with pytest.raises(BundleReferenceError, match="Expected a bundle-local"):
        civic.resolve("https://example.org/object")


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


def test_reference_model_with_list_reference_is_preserved():
    stream = StringIO(
        json.dumps(
            {
                "sequenceReference": {
                    "invalid": {
                        "type": "SequenceReference",
                        "refgetAccession": ["#/sequenceReference/invalid"],
                    },
                }
            }
        )
    )

    bundle = bundles.load_bundle(stream)

    assert bundle.sequenceReference["invalid"]["refgetAccession"] == [
        "#/sequenceReference/invalid"
    ]


def test_reference_model_validation_rejects_non_reference_scalar():
    stream = StringIO(
        json.dumps(
            {
                "sequenceReference": {
                    "invalid": {
                        "type": "SequenceReference",
                        "refgetAccession": 1,
                    },
                }
            }
        )
    )

    with pytest.raises(BundleValidationError):
        bundles.load_bundle(stream)


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
