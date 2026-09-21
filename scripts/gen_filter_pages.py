"""Generate per-axis filter pages for the vignette catalog.

For each unique product, pattern, and implementer value across all vignettes,
emit a page at user-stories/by-<axis>/<value>/index.md that lists the matching
vignettes in the staged documentation tree.
"""

from collections import defaultdict
from collections.abc import Callable, Iterable
from pathlib import Path

from scripts.vignette_loader import load_patterns, load_vignettes, slugify

PRODUCT_ORDER = {"GKS-Core": 0, "VRS": 1, "Cat-VRS": 2, "VA-Spec": 3}


def _product_sort_key(value: str) -> tuple[int, str]:
    """Sort known products in the documentation order, then unknown products alphabetically."""
    return (PRODUCT_ORDER.get(value, len(PRODUCT_ORDER)), value.lower())


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
        {product["name"] for item in vignettes for product in item["products"]},
        key=_product_sort_key,
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
        products_label = " ".join(
            f'<span class="gks-product-label gks-product-label--{slugify(product["name"])}">'
            f"{product['name']}"
            + (
                f" <small>{product['version']}</small>"
                if product.get("version")
                else ""
            )
            + "</span>"
            for product in item["products"]
        )
        lines.extend(
            [
                f"### [{item['title']}]({item['_path']})",
                "",
                f'**Implementer:** {item["implementer"]} · **Pattern:** _{patterns[item["pattern"]]}_ · **Status:** <span class="gks-status gks-status--{item["status"]}">{item["status"]}</span>',
                "",
                f"**Products:** {products_label}",
                "",
                item["summary"],
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
            f.write(f"- **[{title}](../../{v['_path']})** — {summary}\n")


def _emit_axis_index(
    output_root: Path,
    axis: str,
    groups: dict[str, list[dict]],
    patterns: dict[str, str],
) -> None:
    """Emit a landing page for one filter axis."""
    labels = {
        "product": "Browse by product",
        "pattern": "Browse by use pattern",
        "implementer": "Browse by implementer",
    }
    output_path = output_root / f"user-stories/by-{axis}/index.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {labels[axis]}",
        "",
        "Choose a category to browse the matching user stories.",
        "",
    ]
    values = (
        sorted(groups, key=_product_sort_key) if axis == "product" else sorted(groups)
    )
    for value in values:
        label = patterns.get(value, value) if axis == "pattern" else value
        lines.append(f"- [{label}](./{slugify(value)}/index.md)")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
        _emit_axis_index(output_root, axis, groups, patterns_dict)
        for value, matches in groups.items():
            label = patterns_dict.get(value, value) if axis == "pattern" else value
            _emit_filter_page(output_root, axis, slugify(value), label, matches)
