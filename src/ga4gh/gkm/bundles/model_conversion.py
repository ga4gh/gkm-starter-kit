"""Conversion between bundle JSON values and installed GA4GH models."""

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

from .compatibility import supported_gkm_versions, w3id_schema_reference
from .errors import BundleValidationError


@cache
def _model_types() -> dict[str, type[BaseModel]]:
    """Discover concrete models exposed by GA4GH reference packages.

    :return: Models keyed by GKS type discriminator and class name.
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
            if field is not None and isinstance(field.default, str):
                types.setdefault(field.default, candidate)

            types.setdefault(candidate.__name__, candidate)

    return types


def _contains_bundle_reference(value: Any) -> bool:
    """Return whether a value contains a bundle-local JSON Pointer.

    :param value: JSON-compatible value to inspect recursively.
    :return: ``True`` when a bundle-local pointer is present.
    """
    if isinstance(value, str):
        return value.startswith("#/")

    if isinstance(value, Mapping):
        return any(_contains_bundle_reference(item) for item in value.values())

    if isinstance(value, list):
        return any(_contains_bundle_reference(item) for item in value)

    return False


def _only_bundle_reference_errors(error: ValidationError) -> bool:
    """Return whether validation failed exclusively because of local pointers.

    :param error: Pydantic validation error to inspect.
    :return: ``True`` when every error is caused by a bundle-local pointer.
    """
    errors = error.errors()
    return bool(errors) and all(
        detail["type"] != "missing" and _contains_bundle_reference(detail.get("input"))
        for detail in errors
    )


def parse_gks_values(value: Any) -> Any:
    """Convert valid, discriminator-typed mappings to GA4GH models.

    :param value: JSON-compatible value to inspect.
    :return: Reference models where possible, with other values preserved.
    :raises BundleValidationError: If a recognized object is invalid.
    """
    if isinstance(value, list):
        return [parse_gks_values(item) for item in value]

    if not isinstance(value, Mapping):
        return value

    type_name = value.get("type")
    model = _model_types().get(type_name) if isinstance(type_name, str) else None
    if model is None:
        return {key: parse_gks_values(item) for key, item in value.items()}

    try:
        return model.model_validate(value)
    except ValidationError as error:
        if _only_bundle_reference_errors(error):
            return {key: parse_gks_values(item) for key, item in value.items()}

        message = f"Invalid {type_name!r} bundle object: {error}"
        raise BundleValidationError(message) from error


def parse_schema_value(value: Any, model: type[BaseModel]) -> Any:
    """Materialize a schema-selected model unless local pointers prevent it.

    :param value: Value addressed by a bundle-local pointer.
    :param model: Reference implementation selected from the target schema.
    :return: A validated model, or the original value when local pointers prevent it.
    :raises BundleValidationError: If the target is invalid for its schema model.
    """
    try:
        return model.model_validate(value)
    except ValidationError as error:
        if _only_bundle_reference_errors(error):
            return value

        message = f"Invalid {model.__name__!r} bundle object: {error}"
        raise BundleValidationError(message) from error


def model_for_schema_ref(reference: str | None) -> type[BaseModel] | None:
    """Return the installed model identified by a compatible GA4GH W3ID reference.

    :param reference: Schema reference URL, if present.
    :return: Matching reference model, or ``None`` when it is unsupported.
    """
    if reference is None:
        return None

    match = w3id_schema_reference(reference)
    if match is None or match.group("version") != supported_gkm_versions().get(
        match.group("product")
    ):
        return None

    return _model_types().get(reference.rstrip("/").rsplit("/", 1)[-1])


def model_for_schema_references(
    references: tuple[str, ...],
) -> type[BaseModel] | None:
    """Return the first supported model identified by schema references.

    :param references: External schema references in schema order.
    :return: The first matching reference model, or ``None`` when unsupported.
    """
    for reference in references:
        model = model_for_schema_ref(reference)

        if model is not None:
            return model

    return None
