"""Generate the supported GKM product-version table at documentation build time.

The values come from the installed reference implementations through the
package's public compatibility API, so the published documentation reflects
the dependencies used for that specific build.
"""

import mkdocs_gen_files

from ga4gh.gkm.bundles import supported_gkm_versions

OUTPUT_PATH = "library/api/compatibility.md"


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
        "| GKM product | Supported version |",
        "| --- | --- |",
    ]
    lines.extend(
        f"| `{product}` | `{version}` |"
        for product, version in supported_gkm_versions().items()
    )
    lines.extend(
        [
            "",
            "The table is generated during the documentation build from ",
            "`ga4gh.gkm.bundles.supported_gkm_versions()`.",
            "",
            '!!! note "Ballot releases during initial development"',
            "",
            "    During initial development, the supported versions include ",
            "    ballot releases. As GKM products publish stable releases, ",
            "    `ga4gh.gkm` will move to the latest stable versions and stop ",
            "    supporting the superseded ballot releases.",
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


with mkdocs_gen_files.open(OUTPUT_PATH, "w") as output:
    output.write(render_supported_versions())
