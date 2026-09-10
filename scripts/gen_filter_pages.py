"""Generate per-axis filter pages for the vignette catalog.

For each unique product, pattern, and implementer value across all vignettes,
emit a page at user-stories/by-<axis>/<value>/index.md that lists the matching
vignettes in the staged documentation tree.
"""

from collections import defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path

from scripts.vignette_loader import load_patterns, load_vignettes, slugify


def _render_catalog(vignettes: list[dict], patterns: dict[str, str]) -> str:
    lines = [
        "# Pillar III: User Stories",
        "",
        "User stories are the third pillar of the Starter Kit: **real community use cases**, each told as one vignette about who, what problem, and what GKS unlocks, with the actual data and tools. The common thread is always the same: *what a group needs the standards for, and the standards delivering it.*",
        "",
    ]
    if not vignettes:
        lines.append("_No vignettes have been published yet._")
        return "\n".join(lines) + "\n"

    products = sorted(
        {product["name"] for item in vignettes for product in item["products"]}
    )
    pattern_slugs = sorted({item["pattern"] for item in vignettes})
    implementers = sorted({item["implementer"] for item in vignettes})
    lines.extend(
        [
            "## Browse",
            "",
            "**By product:** "
            + " ".join(
                f"[{value}](by-product/{slugify(value)}/index.md){{.gks-chip}}"
                for value in products
            ),
            "",
            "**By pattern:** "
            + " ".join(
                f"[{patterns.get(value, value)}](by-pattern/{slugify(value)}/index.md){{.gks-chip}}"
                for value in pattern_slugs
            ),
            "",
            "**By implementer:** "
            + " ".join(
                f"[{value}](by-implementer/{slugify(value)}/index.md){{.gks-chip}}"
                for value in implementers
            ),
            "",
            "## All user stories",
            "",
        ]
    )
    for item in vignettes:
        products_label = ", ".join(
            " ".join(filter(None, (product["name"], product.get("version", ""))))
            for product in item["products"]
        )
        lines.extend(
            [
                f'### [{item["title"]}]({item["_path"]}) <span class="gks-status gks-status--{item["status"]}">{item["status"]}</span>',
                "",
                f"**{item['implementer']}** · {products_label} · _{patterns.get(item['pattern'], item['pattern'])}_",
                "",
                item["summary"],
                "",
                f"[Read →]({item['_path']})",
                "",
                "---",
                "",
            ]
        )
    return "\n".join(lines)


def _emit_filter_page(
    output_root: Path,
    axis: str,
    value_slug: str,
    value_label: str,
    matches: list[dict],
) -> None:
    output_path = output_root / f"user-stories/by-{axis}/{value_slug}/index.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    headings = {
        "product": f"Vignettes using {value_label}",
        "pattern": f"Vignettes for {value_label}",
        "implementer": f"Vignettes from {value_label}",
    }
    with output_path.open("w", encoding="utf-8") as f:
        f.write(f"# {headings[axis]}\n\n")
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


def main(output_root: Path = Path("docs")) -> None:
    """Generate the vignette filter pages."""
    vignettes = load_vignettes()
    patterns_dict = load_patterns()
    (output_root / "user-stories/index.md").write_text(
        _render_catalog(vignettes, patterns_dict), encoding="utf-8"
    )
    by_axis = {
        "product": _group_by_axis(vignettes, _product_names),
        "pattern": _group_by_axis(vignettes, lambda v: [v.get("pattern", "")]),
        "implementer": _group_by_axis(vignettes, lambda v: [v.get("implementer", "")]),
    }
    for axis, groups in by_axis.items():
        for value, matches in groups.items():
            label = patterns_dict.get(value, value) if axis == "pattern" else value
            _emit_filter_page(output_root, axis, slugify(value), label, matches)
