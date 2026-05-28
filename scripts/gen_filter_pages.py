"""Generate per-axis filter pages for the vignette catalog.

For each unique product, pattern, and implementer value across all vignettes,
emit a virtual page at vignettes/by-<axis>/<value>/index.md that lists the
matching vignettes. mkdocs-gen-files runs this at build time; nothing lands
on disk in docs/.
"""

from collections import defaultdict
from typing import Callable, Iterable

import mkdocs_gen_files

from scripts.vignette_loader import load_patterns, load_vignettes, slugify


def _emit_filter_page(axis: str, value_slug: str, value_label: str, matches: list[dict]) -> None:
    rel_path = f"vignettes/by-{axis}/{value_slug}/index.md"
    with mkdocs_gen_files.open(rel_path, "w") as f:
        f.write(f"# Vignettes filtered by {axis}: {value_label}\n\n")
        if not matches:
            f.write("_No vignettes match this filter yet._\n")
            return
        for v in matches:
            title = v.get("title", v["_folder"])
            summary = v.get("summary", "")
            f.write(f"- **[{title}](../../{v['_folder']}/vignette.md)** — {summary}\n")


def _group_by_axis(
    vignettes: list[dict],
    extract_values: Callable[[dict], Iterable[str]],
) -> dict[str, list[dict]]:
    """Group vignettes by a per-vignette value extractor (may yield 0+ values per vignette)."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for v in vignettes:
        for value in extract_values(v):
            if value:
                groups[value].append(v)
    return groups


def _product_names(v: dict) -> Iterable[str]:
    for p in v.get("products", []) or []:
        if isinstance(p, dict):
            yield p.get("name") or ""
        else:
            yield str(p)


def main() -> None:
    vignettes = load_vignettes()
    patterns_dict = load_patterns()
    by_axis = {
        "product": _group_by_axis(vignettes, _product_names),
        "pattern": _group_by_axis(vignettes, lambda v: [v.get("pattern", "")]),
        "implementer": _group_by_axis(vignettes, lambda v: [v.get("implementer", "")]),
    }
    for axis, groups in by_axis.items():
        for value, matches in groups.items():
            label = patterns_dict.get(value, value) if axis == "pattern" else value
            _emit_filter_page(axis, slugify(value), label, matches)


main()
