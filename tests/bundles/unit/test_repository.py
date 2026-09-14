from pathlib import Path
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
def test_bundle_repository_loads_index_and_resources(get, tmp_path):
    get.side_effect = [
        response_for({"resource_names": ["civic"]}),
        response_for({"objects": {}}),
        response_for({"$schema": "https://json-schema.org/draft/2020-12/schema"}),
    ]

    repository = BundleRepository(data_dir=tmp_path)

    assert repository.resource_names == ("civic",)
    assert repository.get_bundle("civic") == {"objects": {}}
    assert repository.get_bundle_json_schema("civic")["$schema"].startswith("https:")
    assert get.call_args_list[1].args[0].endswith("/civic/bundle.json")
    assert (tmp_path / "index.json").is_file()
    assert (tmp_path / "civic" / "bundle.json").is_file()
    assert (tmp_path / "civic" / "bundle.schema.json").is_file()


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_rejects_unknown_resource(get, tmp_path):
    get.return_value = response_for({"resource_names": ["civic"]})
    repository = BundleRepository(data_dir=tmp_path)

    with pytest.raises(BundleRepositoryResourceNotFoundError):
        repository.get_bundle("missing")


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_rejects_invalid_index(get, tmp_path):
    for index in ({}, {"resource_names": "civic"}, {"resource_names": ["civic", 1]}):
        get.return_value = response_for(index)

        with pytest.raises(BundleRepositoryFormatError):
            BundleRepository(data_dir=tmp_path, refresh=True)


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_rejects_invalid_json(get, tmp_path):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.side_effect = requests.JSONDecodeError("invalid", "", 0)
    get.return_value = response

    with pytest.raises(BundleRepositoryFormatError):
        BundleRepository(data_dir=tmp_path)


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_rejects_non_object_json(get, tmp_path):
    get.return_value = response_for(["civic"])

    with pytest.raises(BundleRepositoryFormatError):
        BundleRepository(data_dir=tmp_path)


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_translates_request_errors(get, tmp_path):
    get.side_effect = requests.RequestException("network unavailable")

    with pytest.raises(BundleRepositoryRequestError):
        BundleRepository(data_dir=tmp_path)


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_reuses_saved_artifacts_without_network(get, tmp_path):
    get.side_effect = [
        response_for({"resource_names": ["civic"]}),
        response_for({"objects": {}}),
        response_for({"$schema": "https://json-schema.org/draft/2020-12/schema"}),
    ]
    repository = BundleRepository(data_dir=tmp_path)
    repository.get_bundle("civic")
    repository.get_bundle_json_schema("civic")

    get.side_effect = requests.RequestException("network unavailable")
    offline_repository = BundleRepository(data_dir=tmp_path)

    assert offline_repository.resource_names == ("civic",)
    assert offline_repository.get_bundle("civic") == {"objects": {}}
    assert offline_repository.get_bundle_json_schema("civic")["$schema"].startswith(
        "https:"
    )


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_bundle_repository_refreshes_index_and_artifacts(get, tmp_path):
    get.side_effect = [
        response_for({"resource_names": ["civic"]}),
        response_for({"objects": {"old": {}}}),
        response_for({"$schema": "old"}),
    ]
    repository = BundleRepository(data_dir=tmp_path)
    repository.get_bundle("civic")
    repository.get_bundle_json_schema("civic")

    get.side_effect = [
        response_for({"resource_names": ["civic", "new"]}),
        response_for({"objects": {"new": {}}}),
        response_for({"$schema": "new"}),
    ]
    refreshed_repository = BundleRepository(data_dir=tmp_path, refresh=True)

    assert refreshed_repository.resource_names == ("civic", "new")
    assert refreshed_repository.get_bundle("civic", refresh=True) == {
        "objects": {"new": {}}
    }
    assert refreshed_repository.get_bundle_json_schema("civic", refresh=True) == {
        "$schema": "new"
    }


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_refresh_keeps_removed_complete_local_resource_loadable(get, tmp_path):
    get.side_effect = [
        response_for({"resource_names": ["civic"]}),
        response_for({"objects": {"saved": {}}}),
        response_for({"$schema": "saved"}),
    ]
    repository = BundleRepository(data_dir=tmp_path)
    repository.get_bundle("civic")
    repository.get_bundle_json_schema("civic")

    get.side_effect = [response_for({"resource_names": []})]
    refreshed_repository = BundleRepository(data_dir=tmp_path, refresh=True)

    assert refreshed_repository.resource_names == ()
    assert refreshed_repository.cached_resource_names == ("civic",)
    assert refreshed_repository.get_bundle("civic") == {"objects": {"saved": {}}}
    assert refreshed_repository.get_bundle_json_schema("civic") == {"$schema": "saved"}


def test_cached_resource_names_preserve_url_encoding(tmp_path):
    (tmp_path / "index.json").write_text('{"resource_names": []}')
    for name in ("name%2Fwith%2Fslashes", "name%20with%20spaces"):
        resource_dir = tmp_path / name
        resource_dir.mkdir()
        (resource_dir / "bundle.json").write_text("{}")
        (resource_dir / "bundle.schema.json").write_text("{}")

    repository = BundleRepository(data_dir=tmp_path)

    assert repository.cached_resource_names == (
        "name%20with%20spaces",
        "name%2Fwith%2Fslashes",
    )


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_failed_refresh_preserves_saved_artifact(get, tmp_path):
    get.side_effect = [
        response_for({"resource_names": ["civic"]}),
        response_for({"objects": {"saved": {}}}),
    ]
    repository = BundleRepository(data_dir=tmp_path)
    assert repository.get_bundle("civic") == {"objects": {"saved": {}}}

    get.side_effect = requests.RequestException("network unavailable")
    with pytest.raises(BundleRepositoryRequestError):
        repository.get_bundle("civic", refresh=True)

    assert repository.get_bundle("civic") == {"objects": {"saved": {}}}


@patch("ga4gh.gkm.bundles.repository.requests.get")
def test_failed_paired_refresh_preserves_both_saved_artifacts(get, tmp_path):
    get.side_effect = [
        response_for({"resource_names": ["civic"]}),
        response_for({"objects": {"old": {}}}),
        response_for({"$schema": "old"}),
    ]
    repository = BundleRepository(data_dir=tmp_path)
    repository.get_bundle_documents("civic")

    get.side_effect = [
        response_for({"objects": {"new": {}}}),
        requests.RequestException("network unavailable"),
    ]
    with pytest.raises(BundleRepositoryRequestError):
        repository.get_bundle_documents("civic", refresh=True)

    assert repository.get_bundle_documents("civic") == (
        {"objects": {"old": {}}},
        {"$schema": "old"},
    )


def test_data_dir_resolution_precedence(monkeypatch, tmp_path):
    explicit_dir = tmp_path / "explicit"
    configured_dir = tmp_path / "configured"
    xdg_dir = tmp_path / "xdg"
    monkeypatch.setenv("GKM_STARTER_KIT_DIR", str(configured_dir))
    monkeypatch.setenv("XDG_DATA_HOME", str(xdg_dir))

    assert BundleRepository._resolve_data_dir(explicit_dir) == explicit_dir  # noqa: SLF001
    assert BundleRepository._resolve_data_dir(None) == configured_dir  # noqa: SLF001

    monkeypatch.delenv("GKM_STARTER_KIT_DIR")
    assert BundleRepository._resolve_data_dir(None) == xdg_dir / "gkm-starter-kit"  # noqa: SLF001

    monkeypatch.delenv("XDG_DATA_HOME")
    assert BundleRepository._resolve_data_dir(None) == (  # noqa: SLF001
        Path.home() / ".local" / "share" / "gkm-starter-kit"
    )
