"""Adapters for constructing models from GA4GH reference implementations."""

# ruff: noqa: ANN401

from __future__ import annotations

import inspect
from collections.abc import Mapping
from functools import cache
from typing import Any

from ga4gh.cat_vrs import models as cat_vrs_models
from ga4gh.core import models as core_models
from ga4gh.va_spec import aac_2017, acmg_2015, base, ccv_2022
from ga4gh.vrs import models as vrs_models
from pydantic import BaseModel, ValidationError

from .errors import BundleValidationError


@cache
def _model_types() -> dict[str, type[BaseModel]]:
    """Discover concrete models exposed by GA4GH reference packages.

    :return: Model classes keyed by their GKS ``type`` value.
    """
    modules = [
        vrs_models,
        cat_vrs_models,
        core_models,
        base,
        aac_2017.models,
        acmg_2015.models,
        ccv_2022.models,
    ]

    types: dict[str, type[BaseModel]] = {}

    for module in modules:
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if not issubclass(candidate, BaseModel) or candidate is BaseModel:
                continue

            field = candidate.model_fields.get("type")
            if field is None or not isinstance(field.default, str):
                continue

            types.setdefault(field.default, candidate)

    return types


def _contains_bundle_reference(value: Any) -> bool:
    """Return whether a value contains a bundle-local JSON Pointer."""
    if isinstance(value, str):
        return value.startswith("#/")
    if isinstance(value, Mapping):
        return any(_contains_bundle_reference(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_bundle_reference(item) for item in value)
    return False


def _only_bundle_reference_errors(error: ValidationError) -> bool:
    """Return whether all errors are consequences of bundle-local references."""
    errors = error.errors()
    return bool(errors) and all(
        detail["type"] != "missing" and _contains_bundle_reference(detail.get("input"))
        for detail in errors
    )


def parse_gks_values(value: Any) -> Any:
    """Convert typed mappings with GA4GH reference implementations.

    The conversion is recursive. Recognized objects must be valid according to
    their installed reference implementation. Objects rejected only because a
    field contains a bundle-local JSON Pointer remain mappings.

    :param value: JSON-compatible value to inspect.
    :return: Reference models where possible, with other values preserved.
    """
    if isinstance(value, list):
        return [parse_gks_values(item) for item in value]

    if not isinstance(value, Mapping):
        return value

    type_name = value.get("type")
    model = _model_types().get(type_name) if isinstance(type_name, str) else None
    if model is not None:
        try:
            return model.model_validate(value)
        except ValidationError as error:
            if _only_bundle_reference_errors(error):
                return {key: parse_gks_values(item) for key, item in value.items()}

            message = f"Invalid {type_name!r} bundle object: {error}"
            raise BundleValidationError(message) from error

    return {key: parse_gks_values(item) for key, item in value.items()}
