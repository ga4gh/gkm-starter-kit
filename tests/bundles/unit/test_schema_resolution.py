"""Unit tests for public producer-schema resolution helpers."""

from ga4gh.va_spec import VASPEC_VERSION

from ga4gh.gkm.bundles.schema_resolution import (
    schema_for_pointer,
    schema_references,
)


def test_schema_resolution_follows_properties_and_local_references():
    """A pointer target resolves through ``properties`` and a local ``$ref``."""
    reference = (
        f"https://w3id.org/ga4gh/schema/va-spec/{VASPEC_VERSION}/base/json/Condition"
    )
    schema = {
        "properties": {
            "conditions": {"$ref": "#/$defs/condition_collection"},
        },
        "$defs": {
            "condition_collection": {
                "properties": {
                    "entry": {"$ref": reference},
                },
            },
        },
    }

    target = schema_for_pointer(schema, ["conditions", "entry"])

    assert target == {"$ref": reference}
    assert schema_references(target, schema) == (reference,)


def test_schema_references_preserves_all_of_order():
    """Composition exposes every external reference for model selection."""
    references = schema_references(
        {
            "allOf": [
                {"$ref": "https://example.org/producer-constraint"},
                {"$ref": "https://example.org/ga4gh-model"},
            ]
        },
        {},
    )

    assert references == (
        "https://example.org/producer-constraint",
        "https://example.org/ga4gh-model",
    )
