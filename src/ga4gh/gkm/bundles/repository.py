"""Access bundles hosted in the public GKM Starter Kit R2 repository.

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

from typing import Any

import requests

from ga4gh.gkm.bundles.errors import (
    BundleRepositoryFormatError,
    BundleRepositoryRequestError,
    BundleRepositoryResourceNotFoundError,
)


class BundleRepository:
    """Access bundles from the canonical GKM Starter Kit R2 repository."""

    base_url: str = "https://pub-489634df77d342208a669f97e449ac4c.r2.dev"

    def __init__(
        self,
        timeout: int = 15,
    ) -> None:
        """Initialize the bundle repository.

        :param timeout: HTTP request timeout in seconds.
        """
        self.timeout = timeout
        self.resource_names = self._list_resource_names()

    def _list_resource_names(self) -> tuple[str, ...]:
        """List the names of bundles available in the repository.

        The repository ``index.json`` is expected to have the form:

            {
                "resource_names": [
                    <NAME_OF_RESOURCE>
                ]
            }

        :return: Names of the available resources.
        :raises BundleRepositoryRequestError: If the index cannot be retrieved.
        :raises BundleRepositoryFormatError: If the index has an invalid format.
        """
        index = self._get_json("index.json")

        resource_names = index.get("resource_names")
        if not isinstance(resource_names, list) or not all(
            isinstance(name, str) for name in resource_names
        ):
            msg = "Bundle repository index must contain a `resource_names` list of strings."
            raise BundleRepositoryFormatError(msg)

        return tuple(resource_names)

    def _verify_resource_exists(self, name: str) -> None:
        """Verify that a bundle resource is listed in the index.

        :param name: Name of the resource
        :raises BundleRepositoryResourceNotFoundError: If the resource is not
            listed in the index.
        """
        if name not in self.resource_names:
            msg = f"Bundle resource name does not exist in index: {name}"
            raise BundleRepositoryResourceNotFoundError(msg)

    def get_bundle(self, name: str) -> dict[str, Any]:
        """Retrieve a bundle.

        :param name: Name of the bundle resource to retrieve.
        :return: Bundle contents.
        :raises BundleRepositoryRequestError: If the bundle cannot be retrieved.
        :raises BundleRepositoryFormatError: If the bundle is not a valid JSON.
        """
        self._verify_resource_exists(name)
        return self._get_json(f"{name}/bundle.json")

    def get_bundle_json_schema(self, name: str) -> dict[str, Any]:
        """Retrieve a bundle JSON Schema.

        :param name: Name of the bundle resource whose JSON Schema should be retrieved.
        :raises BundleRepositoryRequestError: If the schema cannot be retrieved.
        :raises BundleRepositoryFormatError: If the schema is not valid JSON.
        """
        self._verify_resource_exists(name)
        return self._get_json(f"{name}/bundle.schema.json")

    def _get_json(self, path: str) -> dict[str, Any]:
        """Retrieve a JSON object from the repository

        :param path: Path relative to the repository root.
        :return: Parsed JSON object.
        :raises BundleRepositoryRequestError: If the resource cannot be retrieved.
        :raises BundleRepositoryFormatError: If the resource is not a JSON object.
        """
        url = f"{self.base_url}/{path}"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            msg = f"Unable to retrieve bundle repository resource: {url}"
            raise BundleRepositoryRequestError(msg) from e

        try:
            data = response.json()
        except requests.JSONDecodeError as e:
            msg = f"Bundle repository resource is not valid JSON: {url}"
            raise BundleRepositoryFormatError(msg) from e

        if not isinstance(data, dict):
            msg = f"Bundle repository resource must contain a JSON object: {url}"
            raise BundleRepositoryFormatError(msg)

        return data
