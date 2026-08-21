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


def parse_gks_values(value: Any) -> Any:
    """Convert typed mappings with GA4GH reference implementations.

    The conversion is recursive. A mapping remains a mapping when its reference
    model rejects bundle-local JSON Pointer values that it cannot validate as a
    standalone object.

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
        except ValidationError:
            # Producer bundle schemas may use JSON Pointers in fields where a
            # standalone reference model requires an embedded object. Preserve
            # that bundle representation until graph rehydration is requested.
            pass

    return {key: parse_gks_values(item) for key, item in value.items()}
