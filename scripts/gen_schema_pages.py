"""Render committed JSON Schemas to browsable Markdown at build time.

For each docs/data/schemas/*.schema.json, run json-schema-for-humans (md
template) and emit data/schemas/<name>.md via mkdocs-gen-files. Nothing lands
on disk in docs/; the source schema files remain the reviewable source of truth.
"""

import tempfile
from pathlib import Path

import mkdocs_gen_files
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


for schema_path in sorted(SCHEMA_DIR.glob("*.schema.json")):
    name = schema_path.name.replace(".schema.json", "")
    rel = f"data/schemas/{name}.md"
    with mkdocs_gen_files.open(rel, "w") as f:
        f.write(_render(schema_path))
