from unittest.mock import Mock, patch

import pytest
import requests

from ga4gh.gkm.bundles import (
    BundleRepository,
    BundleRepositoryFormatError,
    BundleRepositoryRequestError,
    BundleRepositoryResourceNotFoundError,
)


def response_for(data):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = data
    return response


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_loads_index_and_resources(get):
    get.side_effect = [
        response_for({"resource_names": ["civic"]}),
        response_for({"objects": {}}),
        response_for({"$schema": "https://json-schema.org/draft/2020-12/schema"}),
    ]

    repository = BundleRepository()

    assert repository.resource_names == ("civic",)
    assert repository.get_bundle("civic") == {"objects": {}}
    assert repository.get_bundle_json_schema("civic")["$schema"].startswith("https:")
    assert get.call_args_list[1].args[0].endswith("/civic/bundle.json")


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_rejects_unknown_resource(get):
    get.return_value = response_for({"resource_names": ["civic"]})
    repository = BundleRepository()

    with pytest.raises(BundleRepositoryResourceNotFoundError):
        repository.get_bundle("missing")


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_rejects_invalid_index(get):
    for index in ({}, {"resource_names": "civic"}, {"resource_names": ["civic", 1]}):
        get.return_value = response_for(index)

        with pytest.raises(BundleRepositoryFormatError):
            BundleRepository()


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_rejects_invalid_json(get):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.side_effect = requests.JSONDecodeError("invalid", "", 0)
    get.return_value = response

    with pytest.raises(BundleRepositoryFormatError):
        BundleRepository()


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_rejects_non_object_json(get):
    get.return_value = response_for(["civic"])

    with pytest.raises(BundleRepositoryFormatError):
        BundleRepository()


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_translates_request_errors(get):
    get.side_effect = requests.RequestException("network unavailable")

    with pytest.raises(BundleRepositoryRequestError):
        BundleRepository()
