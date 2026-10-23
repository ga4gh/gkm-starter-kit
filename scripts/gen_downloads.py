"""Generate the Public Repository downloads table."""

import re
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

import requests

from ga4gh.gkm.bundles.repository import BundleRepository

REPOSITORY_PAGE = Path("data/bundle/repository.md")
PLACEHOLDER = "{{ downloads_table }}"
URL_PATTERN = re.compile(r"https?://[^\s<>()]+")


def _linkify_url(match: re.Match[str]) -> str:
    """Wrap a URL in Markdown autolink syntax."""
    url = match.group()
    linked_url = url.rstrip(".,;:!?")
    return f"<{linked_url}>{url[len(linked_url) :]}"


def _schema_description(schema: dict[str, Any]) -> str:
    """Return a schema's top-level description, if present."""
    description = schema.get("description", "")
    return (
        URL_PATTERN.sub(_linkify_url, description)
        if isinstance(description, str)
        else ""
    )


def _get_file_size(url: str) -> str:
    """Fetch file size using an HTTP HEAD request and format it."""
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            return "Unknown"

        headers = {"User-Agent": "Mozilla/5.0 (Python File Size Checker)"}
        response = requests.head(url, headers=headers, timeout=5)

        size_bytes = response.headers.get("Content-Length")
        if size_bytes:
            bytes_float = float(size_bytes)
            for unit in ["B", "KB", "MB", "GB"]:
                if bytes_float < 1000.0:  # noqa: PLR2004
                    return (
                        f"{bytes_float} B"
                        if unit == "B"
                        else f"{bytes_float:.2f} {unit}"
                    )
                bytes_float /= 1000.0
    except requests.RequestException:
        pass
    return "Unknown"


def _render_table(
    resource_names: list[str],
    descriptions: dict[str, str],
    base_url: str,
    bundle_filename: str,
    bundle_schema_filename: str,
) -> str:
    """Render download links derived from the repository index."""
    if not resource_names:
        return "_No downloads are currently available._"

    rows = [
        "| Resource | Bundle Schema Description | Bundle | Schema |",
        "| --- | --- | --- | --- |",
    ]
    for name in resource_names:
        # Resource names are repository path components, not arbitrary URLs.
        path_name = quote(name, safe="")
        resource_url = f"{base_url.rstrip('/')}/{path_name}"

        bundle_url = f"{resource_url}/{bundle_filename}"
        schema_url = f"{resource_url}/{bundle_schema_filename}"

        # Fetch file sizes dynamically
        bundle_size = _get_file_size(bundle_url)
        schema_size = _get_file_size(schema_url)

        rows.append(
            f"| `{name}` | {descriptions.get(name, '')} "
            f"| [Download]({bundle_url}) ({bundle_size}) "
            f"| [Download]({schema_url}) ({schema_size}) |"
        )
    return "\n".join(rows)


def main(output_dir: Path = Path("docs-build")) -> None:
    """Fetch the repository index and inject its downloads table."""
    repository = BundleRepository()
    resource_names = repository.resource_names
    base_url = repository.base_url
    descriptions = {
        name: _schema_description(repository.get_bundle_json_schema(name))
        for name in resource_names
    }

    page = output_dir / REPOSITORY_PAGE
    contents = page.read_text()
    if PLACEHOLDER not in contents:
        msg = "Downloads placeholder not found in repository page"
        raise ValueError(msg)
    generated = _render_table(
        resource_names,
        descriptions,
        base_url,
        repository.bundle_filename,
        repository.bundle_schema_filename,
    )
    page.write_text(contents.replace(PLACEHOLDER, generated, 1))


if __name__ == "__main__":
    main()
