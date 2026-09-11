import json
from io import StringIO
from unittest.mock import Mock

import pytest
from ga4gh.vrs.models import SequenceReference

from ga4gh.gkm import bundles
from ga4gh.gkm.bundles import (
    BundleConflictError,
    BundleNotFoundError,
    BundleRepositoryResourceNotFoundError,
    BundleSerializationError,
)


def test_load_registered_civic_bundle(sequence_id):
    civic = bundles.load_bundle("civic-assertion-9")

    sequence_reference = civic.sequenceReference[sequence_id]

    assert isinstance(civic, bundles.Bundle)
    assert isinstance(sequence_reference, SequenceReference)
    assert sequence_reference.refgetAccession == sequence_id


def test_load_json_stream(sequence_id, sequence_reference_bundle):
    stream = StringIO(json.dumps(sequence_reference_bundle))

    bundle = bundles.load_bundle(stream)

    assert isinstance(bundle.sequenceReference[sequence_id], SequenceReference)


def test_load_repository_bundle_fetches_bundle_and_schema():
    repository = Mock()
    repository.get_bundle.return_value = {"objects": {}}
    repository.get_bundle_json_schema.return_value = {
        "$schema": "https://json-schema.org/draft/2020-12/schema"
    }

    bundle = bundles.load_repository_bundle(repository, "civic")

    assert isinstance(bundle, bundles.Bundle)
    assert bundle.name == "civic"
    repository.get_bundle.assert_called_once_with("civic")
    repository.get_bundle_json_schema.assert_called_once_with("civic")


def test_load_repository_bundle_propagates_unknown_resource():
    repository = Mock()
    repository.get_bundle.side_effect = BundleRepositoryResourceNotFoundError(
        "unknown resource"
    )

    with pytest.raises(BundleRepositoryResourceNotFoundError, match="unknown resource"):
        bundles.load_repository_bundle(repository, "missing")

    repository.get_bundle_json_schema.assert_not_called()


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


def test_load_bundles_rejects_duplicate_names(bundle_dir):
    source = bundle_dir / "civic-assertion-9-bundle.json"

    with pytest.raises(
        BundleConflictError,
        match="Multiple bundles resolved to the name",
    ):
        bundles.load_bundles(source, source)


def test_reject_unsupported_serialization():
    with pytest.raises(BundleSerializationError):
        bundles.load_bundle("civic", serialization="parquet")
