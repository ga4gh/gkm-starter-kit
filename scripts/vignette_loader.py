"""Shared frontmatter loader for the GKS Starter Kit.

Both `main.py` (mkdocs-macros entrypoint) and `scripts/gen_filter_pages.py`
(mkdocs-gen-files script) import from here, so the frontmatter contract has a
single source of truth.
"""

from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
VIGNETTES_DIR = REPO_ROOT / "docs" / "vignettes"
TEMPLATE_FOLDER = "_template"
FRONTMATTER_DELIM = "---"

REQUIRED_FIELDS = (
    "title",
    "slug",
    "summary",
    "products",
    "pattern",
    "implementer",
    "status",
    "last_updated",
)
ALLOWED_STATUSES = ("production", "pilot", "proposal")


def parse_frontmatter(text: str) -> dict | None:
    """Return the YAML frontmatter from a markdown file, or None if absent/invalid."""
    if not text.startswith(FRONTMATTER_DELIM):
        return None
    parts = text.split(FRONTMATTER_DELIM, 2)
    if len(parts) < 3:
        return None
    try:
        meta = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    return meta if isinstance(meta, dict) else None


def slugify(s: str) -> str:
    """Slugify a value for use in URL paths (matches the Jinja filter chain used in the catalog page)."""
    return s.lower().replace(" ", "-").replace("/", "-")


def _validate_vignette(meta: dict, source: Path) -> None:
    """Validate a parsed frontmatter dict; raise ValueError on any problem.

    The error message names the vignette (by `title` if present, else folder)
    and the source file path, so the failing vignette is obvious in build logs.
    """
    rel = source.relative_to(REPO_ROOT) if source.is_absolute() else source
    label = meta.get("title") or source.parent.name

    def fail(problem: str) -> None:
        raise ValueError(f"{label} ({rel}): {problem}")

    for field in REQUIRED_FIELDS:
        if field not in meta or meta[field] in (None, "", []):
            fail(f"missing required field '{field}'")

    products = meta["products"]
    if not isinstance(products, list) or not products:
        fail("'products' must be a non-empty list")
    for i, product in enumerate(products):
        if not isinstance(product, dict):
            fail(f"'products[{i}]' must be a mapping with at least a 'name' key")
        if not product.get("name"):
            fail(f"'products[{i}]' is missing required key 'name'")

    if meta["status"] not in ALLOWED_STATUSES:
        fail(
            f"'status' must be one of {ALLOWED_STATUSES}, got {meta['status']!r}"
        )


def load_vignettes() -> list[dict]:
    """Read every vignette.md under docs/vignettes/<slug>/, returning a list of frontmatter dicts.

    Each returned dict has the original frontmatter plus two synthesized fields:
      - `_folder`: the vignette folder name (matches the `slug` field).
      - `_path`: the relative path used to link to the rendered vignette page.

    Frontmatter is validated; malformed vignettes raise ValueError (fail the build
    with a useful pointer) rather than silently disappearing from the catalog.

    Sorted by `last_updated` descending (newest first), with missing dates sorting last.
    """
    vignettes = []
    for vignette_md in sorted(VIGNETTES_DIR.glob("*/vignette.md")):
        if vignette_md.parent.name == TEMPLATE_FOLDER:
            continue
        meta = parse_frontmatter(vignette_md.read_text(encoding="utf-8"))
        if meta is None:
            raise ValueError(
                f"{vignette_md.relative_to(REPO_ROOT)}: missing or unparseable YAML frontmatter"
            )
        _validate_vignette(meta, vignette_md)
        meta["_folder"] = vignette_md.parent.name
        meta["_path"] = f"{vignette_md.parent.name}/vignette.md"
        vignettes.append(meta)
    vignettes.sort(key=lambda v: str(v.get("last_updated", "")), reverse=True)
    return vignettes
