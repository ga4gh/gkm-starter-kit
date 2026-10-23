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
# Repository bundles hosted on their producer's download site rather than in the
# repository index: (name, bundle URL, schema URL).
EXTERNALLY_HOSTED_BUNDLES = (
    (
        "clinvar-gkm",
        # Stable URL for the newest weekly full bundle.
        "https://data.clinvar-gkm.org/v1/1.1/weekly/clinvar-gkm_00-latest_weekly.json.gz",
        "https://raw.githubusercontent.com/clingen-data-model/clinvar-gkm/main/schema/clinvar-gkm/clinvar-gkm-bundle.schema.json",
    ),
)


def _linkify_url(match: re.Match[str]) -> str:
    """Wrap a URL in Markdown autolink syntax."""
    url = match.group()
    linked_url = url.rstrip(".,;:!?")
    return f"<{linked_url}>{url[len(linked_url) :]}"


def _schema_description(schema: dict[str, Any]) -> str:
    """Return a schema's top-level description, if present."""
    description = schema.get("description", "")
    if not isinstance(description, str):
        return ""
    # Escape angle brackets so literal text such as "<id>" is not read as HTML.
    escaped = description.replace("<", "&lt;").replace(">", "&gt;")
    return URL_PATTERN.sub(_linkify_url, escaped)


def _get_file_size(url: str) -> str:
    """Fetch file size using an HTTP HEAD request and format it."""
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            return "Unknown"

        # Request identity encoding so Content-Length is the uncompressed size.
        headers = {
            "User-Agent": "Mozilla/5.0 (Python File Size Checker)",
            "Accept-Encoding": "identity",
        }
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


def _render_row(name: str, description: str, bundle_url: str, schema_url: str) -> str:
    """Render one downloads table row with dynamically fetched file sizes."""
    return (
        f"| `{name}` | {description} "
        f"| [Download]({bundle_url}) ({_get_file_size(bundle_url)}) "
        f"| [Download]({schema_url}) ({_get_file_size(schema_url)}) |"
    )


def _render_table(
    resource_names: list[str],
    descriptions: dict[str, str],
    base_url: str,
    bundle_filename: str,
    bundle_schema_filename: str,
    extra_rows: list[str] | None = None,
) -> str:
    """Render download links derived from the repository index."""
    rows = []
    for name in resource_names:
        # Resource names are repository path components, not arbitrary URLs.
        path_name = quote(name, safe="")
        resource_url = f"{base_url.rstrip('/')}/{path_name}"

        rows.append(
            _render_row(
                name,
                descriptions.get(name, ""),
                f"{resource_url}/{bundle_filename}",
                f"{resource_url}/{bundle_schema_filename}",
            )
        )
    rows.extend(extra_rows or ())
    if not rows:
        return "_No downloads are currently available._"

    return "\n".join(
        [
            "| Resource | Bundle Schema Description | Bundle | Schema |",
            "| --- | --- | --- | --- |",
            *rows,
        ]
    )


def _render_externally_hosted_rows() -> list[str]:
    """Render download rows for repository bundles hosted by their producers."""
    rows = []
    for name, bundle_url, schema_url in EXTERNALLY_HOSTED_BUNDLES:
        response = requests.get(schema_url, timeout=15)
        response.raise_for_status()
        description = _schema_description(response.json())
        rows.append(_render_row(name, description, bundle_url, schema_url))
    return rows


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
        _render_externally_hosted_rows(),
    )
    page.write_text(contents.replace(PLACEHOLDER, generated, 1))


if __name__ == "__main__":
    main()
