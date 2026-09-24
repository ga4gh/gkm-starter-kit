"""Shared frontmatter loader for the GKM Starter Kit.

The catalog and filter-page generators import from here, so the frontmatter
contract has a single source of truth.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
VIGNETTES_DIR = REPO_ROOT / "docs" / "user-stories"
PATTERNS_YML = VIGNETTES_DIR / "patterns.yml"
TEMPLATE_FOLDER = "_template"
FRONTMATTER_DELIM = "---"
FRONTMATTER_PART_COUNT = 3

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
ALLOWED_PRODUCTS = ("GKS-Core", "VRS", "Cat-VRS", "VA-Spec")


def parse_frontmatter(text: str) -> dict | None:
    """Return the YAML frontmatter from a markdown file, or None if absent/invalid."""
    if not text.startswith(FRONTMATTER_DELIM):
        return None
    parts = text.split(FRONTMATTER_DELIM, 2)
    if len(parts) < FRONTMATTER_PART_COUNT:
        return None
    try:
        meta = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    return meta if isinstance(meta, dict) else None


def slugify(s: str) -> str:
    """Slugify a value for use in URL paths (matches the Jinja filter chain used in the catalog page)."""
    return s.lower().replace(" ", "-").replace("/", "-")


def load_patterns() -> dict[str, str]:
    """Return the pattern vocabulary as a {slug: label} dict, or {} if missing/empty."""
    if not PATTERNS_YML.exists():
        return {}
    with PATTERNS_YML.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def _validate_vignette(
    meta: dict, source: Path, allowed_patterns: dict[str, str] | None = None
) -> None:
    """Validate a parsed frontmatter dict; raise ValueError on any problem.

    The error message names the vignette (by `title` if present, else folder)
    and the source file path, so the failing vignette is obvious in build logs.
    """
    rel = source.relative_to(REPO_ROOT) if source.is_absolute() else source
    label = meta.get("title") or source.parent.name

    def fail(problem: str) -> None:
        msg = f"{label} ({rel}): {problem}"
        raise ValueError(msg)

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
        if product["name"] not in ALLOWED_PRODUCTS:
            fail(
                f"'products[{i}].name' must be one of {ALLOWED_PRODUCTS}, "
                f"got {product['name']!r}"
            )

    if meta["status"] not in ALLOWED_STATUSES:
        fail(f"'status' must be one of {ALLOWED_STATUSES}, got {meta['status']!r}")
    if allowed_patterns is not None and meta["pattern"] not in allowed_patterns:
        fail(
            f"'pattern' must be one of {tuple(allowed_patterns)}, "
            f"got {meta['pattern']!r}"
        )

    notebook = meta.get("notebook")
    if notebook is not None:
        if not isinstance(notebook, dict):
            fail("'notebook' must be a mapping with a 'path' key")
        if not notebook.get("path"):
            fail("'notebook' must include a non-empty 'path' key")
        if not isinstance(notebook["path"], str):
            fail("'notebook.path' must be a string")


def load_vignettes() -> list[dict]:
    """Read every vignette.md under docs/user-stories/<source>/<slug>/, returning a list of frontmatter dicts.

    Each returned dict has the original frontmatter plus two synthesized fields:
      - `_folder`: the source/slug path relative to docs/user-stories.
      - `_path`: the relative path used to link to the rendered vignette page.

    Frontmatter is validated; malformed vignettes raise ValueError (fail the build
    with a useful pointer) rather than silently disappearing from the catalog.

    Sorted by `last_updated` descending (newest first), with missing dates sorting last.
    """
    vignettes = []
    allowed_patterns = load_patterns()
    vignette_paths = sorted(
        {*VIGNETTES_DIR.glob("**/vignette.md"), *VIGNETTES_DIR.glob("**/index.md")}
    )
    for vignette_md in vignette_paths:
        if vignette_md.parent.name == TEMPLATE_FOLDER:
            continue
        meta = parse_frontmatter(vignette_md.read_text(encoding="utf-8"))
        if meta is None:
            msg = f"{vignette_md.relative_to(REPO_ROOT)}: missing or unparseable YAML frontmatter"
            raise ValueError(msg)
        _validate_vignette(meta, vignette_md, allowed_patterns)
        if vignette_md.name == "index.md" and vignette_md.parent.name == "vignette":
            folder = vignette_md.parent.parent.relative_to(VIGNETTES_DIR)
            path = f"{folder}/vignette/index.md"
        else:
            folder = vignette_md.parent.relative_to(VIGNETTES_DIR)
            path = f"{folder}/{vignette_md.name}"
        meta["_folder"] = str(folder)
        meta["_path"] = path
        vignettes.append(meta)
    vignettes.sort(key=lambda v: str(v.get("last_updated", "")), reverse=True)
    return vignettes
