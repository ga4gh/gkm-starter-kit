"""Unit tests for public GA4GH model-conversion helpers."""

from ga4gh.core.models import MappableConcept
from ga4gh.va_spec import VASPEC_VERSION
from ga4gh.va_spec.base import Condition

from ga4gh.gkm.bundles.model_conversion import (
    model_for_schema_ref,
    model_for_schema_references,
    parse_schema_value,
)


def test_model_for_schema_ref_selects_the_installed_va_spec_model():
    """A compatible W3ID reference selects its installed Pydantic model."""
    reference = (
        f"https://w3id.org/ga4gh/schema/va-spec/{VASPEC_VERSION}/base/json/Condition"
    )

    assert model_for_schema_ref(reference) is Condition


def test_model_for_schema_references_skips_unrecognized_references():
    """The first compatible GA4GH reference selects the target model."""
    reference = (
        f"https://w3id.org/ga4gh/schema/va-spec/{VASPEC_VERSION}/base/json/Condition"
    )

    assert (
        model_for_schema_references(
            ("https://example.org/producer-constraint", reference)
        )
        is Condition
    )


def test_parse_schema_value_validates_nested_va_spec_models():
    """Schema-selected values receive normal nested Pydantic conversion."""
    condition = parse_schema_value({"name": "Example"}, Condition)

    assert isinstance(condition, Condition)
    assert isinstance(condition.root, MappableConcept)
