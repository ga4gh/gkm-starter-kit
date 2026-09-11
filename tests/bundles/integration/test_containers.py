import json
from io import StringIO

import pytest
from ga4gh.cat_vrs.models import CategoricalVariant
from ga4gh.core.models import MappableConcept
from ga4gh.va_spec.base import Condition

from ga4gh.gkm import bundles
from ga4gh.gkm.bundles import (
    BundleSerializationError,
)


def test_collection_names(sequence_id):
    civic = bundles.load_bundle("civic-assertion-9")

    assert civic.collection_names() == tuple(civic.keys())
    assert civic.collection_names()[0] == "sequenceReference"
    assert "assertion" in civic.collection_names()
    assert sequence_id in list(civic.sequenceReference.keys())


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


def test_normalize():
    civic = bundles.load_bundle("civic-assertion-251")

    inline = civic.normalize()

    assertion = inline["assertion"]["civic.aid:251"]
    assert assertion["proposition"]["type"] == "VariantOncogenicityProposition"
    assert civic.to_dict()["assertion"]["civic.aid:251"]["proposition"].startswith("#/")


def test_normalize_from_value():
    civic = bundles.load_bundle("civic-assertion-9")
    proposition = civic.resolve(civic.assertion["civic.aid:9"]["proposition"])

    inline = civic.normalize(proposition)

    assert inline["type"] == "VariantClinicalSignificanceProposition"
    assert isinstance(inline["subjectVariant"], dict)


def test_resolve_accepts_iri_references_and_nested_root(bundle_dir):
    civic = bundles.load_bundle(
        bundle_dir / "civic-assertion-9-bundle.json",
        schema=bundle_dir / "civic-gks-bundle-v0.1.0.schema.json",
    )
    assertion = civic.assertion[next(iter(civic.assertion))]
    proposition = civic.resolve(assertion["proposition"])

    subject_variant = civic.resolve(proposition.subjectVariant)
    assert isinstance(subject_variant, CategoricalVariant)
    assert civic.resolve(proposition.subjectVariant.root) == subject_variant

    object_condition = civic.resolve(proposition.objectCondition)
    assert isinstance(object_condition, Condition)
    assert isinstance(object_condition.root, MappableConcept)
    assert civic.resolve(proposition.objectCondition.root) == object_condition


def test_resolve_uses_the_target_schema_not_the_collection_schema(bundle_dir):
    """A nested pointer must not be materialized as its enclosing Statement."""
    civic = bundles.load_bundle(
        bundle_dir / "civic-assertion-9-bundle.json",
        schema=bundle_dir / "civic-gks-bundle-v0.1.0.schema.json",
    )

    strength = civic.resolve("#/evidence/civic.eid:4846/strength")

    assert isinstance(strength, dict)
    assert strength["name"] == "Clinical evidence"


def test_resolve_follows_local_schema_reference_from_properties():
    """A target schema in ``$defs`` materializes an ordinary property value."""
    schema = {
        "properties": {
            "conditions": {"$ref": "#/$defs/condition_collection"},
        },
        "$defs": {
            "condition_collection": {
                "properties": {
                    "entry": {"$ref": "#/$defs/condition"},
                },
            },
            "condition": {
                "$ref": (
                    "https://w3id.org/ga4gh/schema/va-spec/"
                    "1.1.0-snapshot.2026-06.1/base/json/Condition"
                )
            },
        },
    }

    document = {"conditions": {"entry": {"name": "Example"}}}

    bundle = bundles.load_bundle(
        StringIO(json.dumps(document)),
        schema=StringIO(json.dumps(schema)),
    )

    condition = bundle.resolve("#/conditions/entry")

    assert isinstance(condition, Condition)
    assert isinstance(condition.root, MappableConcept)


def test_resolve_follows_schema_items_for_array_elements():
    """Array-element pointers use ``items`` or ``prefixItems`` schemas."""
    schema = {
        "properties": {
            "examples": {
                "properties": {
                    "entry": {
                        "properties": {
                            "conditions": {
                                "items": {
                                    "$ref": (
                                        "https://w3id.org/ga4gh/schema/va-spec/"
                                        "1.1.0-snapshot.2026-06.1/base/json/Condition"
                                    )
                                },
                                "type": "array",
                            },
                            "featured": {
                                "prefixItems": [
                                    {
                                        "$ref": (
                                            "https://w3id.org/ga4gh/schema/va-spec/"
                                            "1.1.0-snapshot.2026-06.1/base/json/Condition"
                                        )
                                    }
                                ],
                                "type": "array",
                            },
                        }
                    }
                }
            }
        },
    }

    document = {
        "examples": {
            "entry": {
                "conditions": [{"name": "Example"}],
                "featured": [{"name": "Featured example"}],
            },
        },
    }

    bundle = bundles.load_bundle(
        StringIO(json.dumps(document)),
        schema=StringIO(json.dumps(schema)),
    )

    condition = bundle.resolve("#/examples/entry/conditions/0")
    featured_condition = bundle.resolve("#/examples/entry/featured/0")

    assert isinstance(condition, Condition)
    assert isinstance(condition.root, MappableConcept)
    assert isinstance(featured_condition, Condition)
    assert isinstance(featured_condition.root, MappableConcept)


def test_resolve_follows_additional_properties_schema():
    """A property covered by ``additionalProperties`` uses that target schema."""
    schema = {
        "properties": {
            "conditions": {
                "additionalProperties": {
                    "$ref": (
                        "https://w3id.org/ga4gh/schema/va-spec/"
                        "1.1.0-snapshot.2026-06.1/base/json/Condition"
                    )
                }
            }
        }
    }
    document = {"conditions": {"producer-defined": {"name": "Example"}}}

    bundle = bundles.load_bundle(
        StringIO(json.dumps(document)),
        schema=StringIO(json.dumps(schema)),
    )

    condition = bundle.resolve("#/conditions/producer-defined")

    assert isinstance(condition, Condition)
    assert isinstance(condition.root, MappableConcept)


def test_resolve_selects_a_ga4gh_reference_from_all_of():
    """A non-GA4GH constraint must not hide a later GA4GH model reference."""
    schema = {
        "properties": {
            "conditions": {
                "properties": {
                    "entry": {
                        "allOf": [
                            {"$ref": "https://example.org/producer-constraint"},
                            {
                                "$ref": (
                                    "https://w3id.org/ga4gh/schema/va-spec/"
                                    "1.1.0-snapshot.2026-06.1/base/json/Condition"
                                )
                            },
                        ]
                    }
                }
            }
        }
    }
    document = {"conditions": {"entry": {"name": "Example"}}}

    bundle = bundles.load_bundle(
        StringIO(json.dumps(document)),
        schema=StringIO(json.dumps(schema)),
    )

    condition = bundle.resolve("#/conditions/entry")

    assert isinstance(condition, Condition)
    assert isinstance(condition.root, MappableConcept)


def test_normalize_and_export_round_trip():
    civic = bundles.load_bundle("civic-assertion-9")
    original = civic.assertion["civic.aid:9"]

    normalized = civic.normalize(original)
    exported = civic.export(normalized)
    deep_exported = civic.export(original, deep=True)

    assert exported["proposition"] == original["proposition"]
    assert exported["id"] == "civic.aid:9"
    assert isinstance(deep_exported["proposition"], dict)


def test_denormalize_replaces_nested_objects_by_content_or_identity(sequence_id):
    """Denormalization uses generic bundle identity rules, not producer names."""
    civic = bundles.load_bundle("civic-assertion-9")
    sequence = civic.sequenceReference[sequence_id].model_dump(
        mode="json", exclude_none=True
    )
    assertion = dict(civic.assertion["civic.aid:9"])
    normalized = {
        "sequence": sequence,
        "updated_assertion": {**assertion, "description": "updated"},
        "producer_object": {"id": "producer-1", "type": "OtherObject"},
    }

    exported = civic.denormalize(normalized)

    assert exported["sequence"] == f"#/sequenceReference/{sequence_id}"
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
