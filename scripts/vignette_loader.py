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


def load_vignettes() -> list[dict]:
    """Read every vignette.md under docs/vignettes/<slug>/, returning a list of frontmatter dicts.

    Each returned dict has the original frontmatter plus two synthesized fields:
      - `_folder`: the vignette folder name (matches the `slug` field).
      - `_path`: the relative path used to link to the rendered vignette page.

    Sorted by `last_updated` descending (newest first), with missing dates sorting last.
    """
    vignettes = []
    for vignette_md in sorted(VIGNETTES_DIR.glob("*/vignette.md")):
        if vignette_md.parent.name == TEMPLATE_FOLDER:
            continue
        meta = parse_frontmatter(vignette_md.read_text(encoding="utf-8"))
        if meta is None:
            continue
        meta["_folder"] = vignette_md.parent.name
        meta["_path"] = f"{vignette_md.parent.name}/vignette.md"
        vignettes.append(meta)
    vignettes.sort(key=lambda v: str(v.get("last_updated", "")), reverse=True)
    return vignettes
