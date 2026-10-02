"""Generate the supported GKM product-version table at documentation build time.

The values come from the installed reference implementations through the
package's public compatibility API, so the published documentation reflects
the dependencies used for that specific build.
"""

from pathlib import Path

from ga4gh.gkm.bundles import supported_gkm_versions

OUTPUT_PATH = Path("tools/gkm-toolkit/api/compatibility.md")
TOOLKIT_INDEX_PATH = Path("tools/gkm-toolkit/index.md")
TABLE_MARKER = "{{ supported_product_versions_table }}"


def render_supported_versions_table() -> list[str]:
    """Render the supported GKM product-version table."""
    lines = [
        "| GKM product | Supported version |",
        "| --- | --- |",
    ]
    lines.extend(
        f"| `{product}` | `{version}` |"
        for product, version in supported_gkm_versions().items()
    )
    return lines


def render_supported_versions() -> str:
    """Render the supported product versions as a Markdown page."""
    lines = [
        "# Compatibility",
        "",
        "A bundle schema must use the GKM product versions supported by the ",
        "installed `ga4gh.gkm` release. Loading fails when a recognized GKM ",
        "schema reference uses a different version.",
        "",
        "## Supported product versions",
        "",
        "`ga4gh.gkm` currently supports:",
        "",
    ]
    lines.extend(render_supported_versions_table())
    lines.extend(
        [
            "",
            "The table is generated during the documentation build from ",
            "`ga4gh.gkm.bundles.supported_gkm_versions()`.",
            "",
            "## API",
            "",
            "::: ga4gh.gkm.bundles.compatibility",
            "    options:",
            '      filters: ["!^_[^_]", "!^[A-Z]"]',
            "      show_root_heading: true",
            "      show_root_full_path: false",
            "      show_object_full_path: false",
            "      show_category_heading: true",
        ]
    )
    return "\n".join(lines)


def main(output_root: Path = Path("docs")) -> None:
    """Write supported-version documentation into the documentation tree."""
    output_path = output_root / OUTPUT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_supported_versions(), encoding="utf-8")

    toolkit_index_path = output_root / TOOLKIT_INDEX_PATH
    toolkit_index = toolkit_index_path.read_text(encoding="utf-8")
    supported_versions_table = "\n".join(render_supported_versions_table())
    toolkit_index_path.write_text(
        toolkit_index.replace(TABLE_MARKER, supported_versions_table), encoding="utf-8"
    )
