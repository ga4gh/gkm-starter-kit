"""Render committed JSON Schemas to browsable Markdown at build time.

For each docs/data/schemas/*.schema.json, run json-schema-for-humans (md
template) and emit data/bundle-schemas/<name>.md in the staged documentation tree.
"""

import tempfile
from pathlib import Path

from json_schema_for_humans.generate import generate_from_filename
from json_schema_for_humans.generation_configuration import GenerationConfiguration

SCHEMA_DIR = Path("docs/data/schemas")
CONFIG = GenerationConfiguration(
    template_name="md",
    show_toc=True,
    copy_css=False,
    copy_js=False,
)


def _render(schema_path: Path) -> str:
    with tempfile.NamedTemporaryFile("r+", suffix=".md", delete=True) as tmp:
        generate_from_filename(str(schema_path), tmp.name, config=CONFIG)
        tmp.seek(0)
        return tmp.read()


def main(output_root: Path = Path("docs")) -> None:
    """Render schema reference pages into the documentation tree."""
    for schema_path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        name = schema_path.name.replace(".schema.json", "")
        output_path = output_root / f"data/bundle-schemas/{name}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(_render(schema_path), encoding="utf-8")
