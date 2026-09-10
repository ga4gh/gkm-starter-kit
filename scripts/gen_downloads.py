"""Generate the Public Repository downloads table."""

from pathlib import Path
from urllib.parse import quote

from ga4gh.gkm.bundles import BundleRepository

REPOSITORY_PAGE = Path("data/bundle-repository.md")
PLACEHOLDER = "{{ downloads_table }}"


def _render_table(
    resource_names: list[str],
    base_url: str,
    bundle_filename: str,
    bundle_schema_filename: str,
) -> str:
    """Render download links derived from the repository index."""
    if not resource_names:
        return "_No downloads are currently available._"

    rows = ["| Resource | Bundle | Schema |", "| --- | --- | --- |"]
    for name in resource_names:
        # Resource names are repository path components, not arbitrary URLs.
        path_name = quote(name, safe="")
        resource_url = f"{base_url.rstrip('/')}/{path_name}"
        rows.append(
            f"| `{name}` | [Download]({resource_url}/{bundle_filename}) "
            f"| [Download]({resource_url}/{bundle_schema_filename}) |"
        )
    return "\n".join(rows)


def main(output_dir: Path = Path("docs-build")) -> None:
    """Fetch the repository index and inject its downloads table."""
    repository = BundleRepository()
    resource_names = repository.resource_names
    base_url = repository.base_url

    page = output_dir / REPOSITORY_PAGE
    contents = page.read_text()
    if PLACEHOLDER not in contents:
        msg = "Downloads placeholder not found in repository page"
        raise ValueError(msg)
    generated = _render_table(
        resource_names,
        base_url,
        repository.bundle_filename,
        repository.bundle_schema_filename,
    )
    page.write_text(contents.replace(PLACEHOLDER, generated, 1))


if __name__ == "__main__":
    main()
