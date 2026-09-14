"""Access and persist bundles hosted in the public GKM Starter Kit repository.

The repository index and every retrieved bundle artifact are stored locally so
published data remains usable after it has been fetched once.

The initial implementation makes the following assumptions:

* The repository root contains an ``index.json`` file listing available resource
  names.
* Each resource directory contains exactly two files: ``bundle.json`` and
  ``bundle.schema.json``.

For example, the expected repository layout is:

    /
    ├── index.json
    ├── civic/
    │   ├── bundle.json
    │   └── bundle.schema.json
"""

from __future__ import annotations

import json
import os
from os import PathLike
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any
from urllib.parse import quote, unquote

import requests

from ga4gh.gkm.bundles.errors import (
    BundleRepositoryFormatError,
    BundleRepositoryRequestError,
    BundleRepositoryResourceNotFoundError,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class BundleRepository:
    """Access bundles from the canonical GKM Starter Kit R2 repository.

    Repository documents are persisted in :attr:`data_dir`, selected in this
    order:

    1. An explicit ``data_dir`` argument.
    2. The ``GKM_STARTER_KIT_DIR`` environment variable.
    3. ``XDG_DATA_HOME/gkm-starter-kit``.
    4. ``~/.local/share/gkm-starter-kit``.

    The saved ``index.json`` is reused by default, which permits offline
    construction after the index has been retrieved once. Pass ``refresh=True``
    to retrieve and atomically replace the saved index.

    :attr:`resource_names` reflects the saved or refreshed repository index.
    :attr:`cached_resource_names` lists complete locally saved resources,
    including resources subsequently removed from a refreshed remote index.
    """

    base_url: str = "https://pub-489634df77d342208a669f97e449ac4c.r2.dev"
    bundle_filename: str = "bundle.json"
    bundle_schema_filename: str = "bundle.schema.json"
    index_filename: str = "index.json"

    def __init__(
        self,
        timeout: int = 15,
        *,
        data_dir: str | PathLike[str] | None = None,
        refresh: bool = False,
    ) -> None:
        """Initialize the bundle repository and load its resource index.

        :param timeout: HTTP request timeout in seconds.
        :param data_dir: Directory for persisted repository documents. When
            omitted, the directory is derived from the environment and XDG
            data-directory conventions.
        :param refresh: When true, retrieve and replace the saved index rather
            than reuse it.
        :raises BundleRepositoryRequestError: If a required index cannot be
            retrieved from the repository.
        :raises BundleRepositoryFormatError: If the saved or retrieved index
            is not a JSON object with a ``resource_names`` string list.
        """
        self.timeout = timeout
        self.data_dir = self._resolve_data_dir(data_dir)
        self.resource_names = self._list_resource_names(refresh=refresh)

    @property
    def cached_resource_names(self) -> tuple[str, ...]:
        """Return complete resource artifacts available in local storage.

        A cached resource has both ``bundle.json`` and
        ``bundle.schema.json``. It remains available here and can be loaded
        even if a later refreshed repository index no longer lists it.

        :return: Locally saved resource names in alphabetical order.
        """
        if not self.data_dir.is_dir():
            return ()

        names = [
            unquote(path.name)
            for path in self.data_dir.iterdir()
            if path.is_dir()
            and (path / self.bundle_filename).is_file()
            and (path / self.bundle_schema_filename).is_file()
        ]
        return tuple(sorted(names))

    @staticmethod
    def _resolve_data_dir(data_dir: str | PathLike[str] | None) -> Path:
        """Determine the directory used for persisted repository documents.

        :param data_dir: Explicit data directory, if supplied.
        :return: Expanded path selected from the explicit value, environment,
            or the default XDG-compatible location.
        """
        if data_dir is not None:
            return Path(data_dir).expanduser()

        configured_dir = os.environ.get("GKM_STARTER_KIT_DIR")
        if configured_dir:
            return Path(configured_dir).expanduser()

        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        if xdg_data_home:
            return Path(xdg_data_home).expanduser() / "gkm-starter-kit"

        return Path.home() / ".local" / "share" / "gkm-starter-kit"

    def _list_resource_names(self, *, refresh: bool) -> tuple[str, ...]:
        """List names published by the repository index.

        The repository ``index.json`` has the form:

            {
                "resource_names": [
                    <NAME_OF_RESOURCE>
                ]
            }

        :param refresh: Whether to replace a locally saved index from the
            remote repository.
        :return: Names of available resources.
        :raises BundleRepositoryRequestError: If a missing or refreshed index
            cannot be retrieved.
        :raises BundleRepositoryFormatError: If the index has an invalid format.
        """
        index = self._get_json(
            self.index_filename,
            refresh=refresh,
            validator=self._validate_index,
        )
        return tuple(index["resource_names"])

    @staticmethod
    def _validate_index(index: dict[str, Any]) -> None:
        """Validate the repository-specific structure of an index document.

        :param index: Parsed repository index document.
        :raises BundleRepositoryFormatError: If the index lacks a
            ``resource_names`` list of strings.
        """
        resource_names = index.get("resource_names")
        if not isinstance(resource_names, list) or not all(
            isinstance(name, str) for name in resource_names
        ):
            msg = "Bundle repository index must contain a `resource_names` list of strings."
            raise BundleRepositoryFormatError(msg)

    def _verify_resource_exists(self, name: str) -> None:
        """Verify that a bundle resource is indexed or completely cached locally.

        :param name: Name of the resource.
        :raises BundleRepositoryResourceNotFoundError: If the resource is not
            listed in the index and does not have both saved artifacts.
        """
        if name not in self.resource_names and name not in self.cached_resource_names:
            msg = f"Bundle resource is neither indexed nor completely saved locally: {name}"
            raise BundleRepositoryResourceNotFoundError(msg)

    def get_bundle(self, name: str, *, refresh: bool = False) -> dict[str, Any]:
        """Retrieve a bundle, preferring its saved local copy.

        :param name: Name of the bundle resource to retrieve.
        :param refresh: When true, retrieve and atomically replace the saved
            bundle instead of reusing it. A refresh requires the remote resource
            to remain available.
        :return: Bundle contents.
        :raises BundleRepositoryResourceNotFoundError: If ``name`` is absent
            from the repository index and does not have both saved artifacts.
        :raises BundleRepositoryRequestError: If a missing or refreshed bundle
            cannot be retrieved.
        :raises BundleRepositoryFormatError: If the saved or retrieved bundle
            is not a JSON object.
        """
        self._verify_resource_exists(name)
        return self._get_json(
            f"{quote(name, safe='')}/{self.bundle_filename}", refresh=refresh
        )

    def get_bundle_json_schema(
        self, name: str, *, refresh: bool = False
    ) -> dict[str, Any]:
        """Retrieve a bundle JSON Schema, preferring its saved local copy.

        :param name: Name of the bundle resource whose JSON Schema to retrieve.
        :param refresh: When true, retrieve and atomically replace the saved
            schema instead of reusing it. A refresh requires the remote resource
            to remain available.
        :return: Bundle JSON Schema contents.
        :raises BundleRepositoryResourceNotFoundError: If ``name`` is absent
            from the repository index and does not have both saved artifacts.
        :raises BundleRepositoryRequestError: If a missing or refreshed schema
            cannot be retrieved.
        :raises BundleRepositoryFormatError: If the saved or retrieved schema
            is not a JSON object.
        """
        self._verify_resource_exists(name)
        return self._get_json(
            f"{quote(name, safe='')}/{self.bundle_schema_filename}", refresh=refresh
        )

    def get_bundle_documents(
        self, name: str, *, refresh: bool = False
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Retrieve a bundle and schema together.

        Missing or refreshed artifacts are both downloaded and validated before
        either local file is replaced. Each artifact is written atomically.

        :param name: Name of the bundle resource to retrieve.
        :param refresh: When true, retrieve and replace both saved artifacts.
            A refresh requires the remote resource to remain available.
        :return: Bundle contents and its JSON Schema, in that order.
        :raises BundleRepositoryResourceNotFoundError: If ``name`` is absent
            from the repository index and does not have both saved artifacts.
        :raises BundleRepositoryRequestError: If either required remote artifact
            cannot be retrieved.
        :raises BundleRepositoryFormatError: If a saved or retrieved artifact
            is not a JSON object.
        """
        self._verify_resource_exists(name)
        bundle_path = f"{quote(name, safe='')}/{self.bundle_filename}"
        schema_path = f"{quote(name, safe='')}/{self.bundle_schema_filename}"
        cached_bundle_path = self._cache_path(bundle_path)
        cached_schema_path = self._cache_path(schema_path)

        if (
            not refresh
            and cached_bundle_path.is_file()
            and cached_schema_path.is_file()
        ):
            return (
                self._read_cached_json(cached_bundle_path),
                self._read_cached_json(cached_schema_path),
            )

        bundle = self._download_json(bundle_path)
        schema = self._download_json(schema_path)
        self._write_cached_pair(
            cached_bundle_path,
            bundle,
            cached_schema_path,
            schema,
        )
        return bundle, schema

    def _cache_path(self, path: str) -> Path:
        """Return the local path for a repository-relative artifact path.

        :param path: Repository-relative, URL-encoded artifact path.
        :return: Corresponding path below :attr:`data_dir`.
        """
        return self.data_dir.joinpath(*path.split("/"))

    def _get_json(
        self,
        path: str,
        *,
        refresh: bool,
        validator: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        """Load a JSON object from local storage or the remote repository.

        :param path: Repository-relative artifact path.
        :param refresh: Whether to bypass and replace a locally saved artifact.
        :param validator: Optional repository-specific validation performed
            before a downloaded document replaces its local copy.
        :return: Parsed JSON object.
        :raises BundleRepositoryRequestError: If a required remote artifact
            cannot be retrieved.
        :raises BundleRepositoryFormatError: If an artifact is not a JSON object.
        """
        cache_path = self._cache_path(path)
        if cache_path.is_file() and not refresh:
            data = self._read_cached_json(cache_path)
            if validator is not None:
                validator(data)
            return data

        data = self._download_json(path)
        if validator is not None:
            validator(data)
        self._write_cached_json(cache_path, data)
        return data

    @staticmethod
    def _read_cached_json(cache_path: Path) -> dict[str, Any]:
        """Read and validate a locally persisted JSON object.

        :param cache_path: Artifact file to read.
        :return: Parsed JSON object.
        :raises BundleRepositoryFormatError: If the artifact is unreadable,
            invalid JSON, or not a JSON object.
        """
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            msg = f"Saved bundle repository resource is not valid JSON: {cache_path}"
            raise BundleRepositoryFormatError(msg) from error

        if not isinstance(data, dict):
            msg = f"Saved bundle repository resource must contain a JSON object: {cache_path}"
            raise BundleRepositoryFormatError(msg)
        return data

    def _download_json(self, path: str) -> dict[str, Any]:
        """Retrieve and validate a JSON object from the remote repository.

        :param path: Repository-relative artifact path.
        :return: Parsed JSON object.
        :raises BundleRepositoryRequestError: If the artifact cannot be retrieved.
        :raises BundleRepositoryFormatError: If the artifact is not a JSON object.
        """
        url = f"{self.base_url}/{path}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as error:
            msg = f"Unable to retrieve bundle repository resource: {url}"
            raise BundleRepositoryRequestError(msg) from error

        try:
            data = response.json()
        except requests.JSONDecodeError as error:
            msg = f"Bundle repository resource is not valid JSON: {url}"
            raise BundleRepositoryFormatError(msg) from error

        if not isinstance(data, dict):
            msg = f"Bundle repository resource must contain a JSON object: {url}"
            raise BundleRepositoryFormatError(msg)
        return data

    @staticmethod
    def _write_cached_json(cache_path: Path, data: dict[str, Any]) -> None:
        """Atomically save a validated JSON object to local storage.

        The temporary file is completely written before replacement, preventing
        an interrupted write from leaving a truncated cached artifact.

        :param cache_path: Artifact file to replace.
        :param data: Validated JSON object to serialize.
        """
        temporary_path = BundleRepository._write_json_temporary_file(cache_path, data)
        try:
            temporary_path.replace(cache_path)
        finally:
            temporary_path.unlink(missing_ok=True)

    @staticmethod
    def _write_json_temporary_file(cache_path: Path, data: dict[str, Any]) -> Path:
        """Serialize a JSON object to a temporary file beside its destination.

        :param cache_path: Final destination for the serialized JSON object.
        :param data: Validated JSON object to serialize.
        :return: Closed temporary file in the destination directory.
        """
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=cache_path.parent, delete=False
        ) as temporary_file:
            temporary_file.write(json.dumps(data, indent=2) + "\n")
            return Path(temporary_file.name)

    @staticmethod
    def _write_cached_pair(
        bundle_path: Path,
        bundle: dict[str, Any],
        schema_path: Path,
        schema: dict[str, Any],
    ) -> None:
        """Atomically replace each artifact in a bundle/schema pair.

        :param bundle_path: Cached bundle destination.
        :param bundle: Validated bundle JSON object.
        :param schema_path: Cached schema destination.
        :param schema: Validated schema JSON object.
        """
        BundleRepository._write_cached_json(bundle_path, bundle)
        BundleRepository._write_cached_json(schema_path, schema)
