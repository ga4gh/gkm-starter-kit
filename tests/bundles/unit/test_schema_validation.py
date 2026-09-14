import pytest

from ga4gh.gkm.bundles.errors import BundleSerializationError, BundleValidationError
from ga4gh.gkm.bundles.pointers import validate_and_expand_bundle_references
from ga4gh.gkm.bundles.schema_validation import validate_bundle_schema


def test_validate_bundle_schema_accepts_valid_document():
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
    }

    validate_bundle_schema({"name": "example"}, schema)


def test_validate_bundle_schema_reports_instance_path():
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"objects": {"type": "object"}},
    }

    with pytest.raises(
        BundleValidationError,
        match=r"objects: 1 is not of type 'object'",
    ):
        validate_bundle_schema({"objects": 1}, schema)


def test_validate_bundle_schema_rejects_invalid_schema():
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "not-a-json-schema-type",
    }

    with pytest.raises(BundleSerializationError, match="Invalid bundle JSON Schema"):
        validate_bundle_schema({}, schema)


def test_validate_bundle_schema_rejects_non_draft_202012_schema():
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
    }

    with pytest.raises(BundleSerializationError, match="must declare Draft 2020-12"):
        validate_bundle_schema({}, schema)


def test_validate_bundle_schema_preserves_schema_id_for_self_references():
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:example:bundle-schema",
        "type": "object",
        "properties": {"name": {"$ref": "urn:example:bundle-schema#/$defs/name"}},
        "$defs": {"name": {"type": "string"}},
    }

    validate_bundle_schema({"name": "example"}, schema)


def test_validate_bundle_schema_expands_local_bundle_references():
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "objects": {
                "type": "object",
                "additionalProperties": {"$ref": "#/$defs/object"},
            }
        },
        "$defs": {
            "object": {
                "type": "object",
                "required": ["id"],
                "properties": {"id": {"type": "string"}},
            }
        },
    }

    expanded = validate_and_expand_bundle_references(
        {"objects": {"one": {"id": "one"}, "alias": "#/objects/one"}}
    )
    validate_bundle_schema(expanded, schema)
