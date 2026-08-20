"""Publish and render the CIViC notebook in the documentation site."""

import json
from pathlib import Path
from typing import Any

import mkdocs_gen_files

from scripts.bundle_examples import BUNDLE_OUTPUT_DIR, discover_example_paths

SOURCE_DIR = Path("notebooks/civic")
NOTEBOOK = SOURCE_DIR / "explore-civic-buns.ipynb"
NOTEBOOK_PAGE = Path("library/civic-notebook.md")


def _text(value: str | list[str]) -> str:
    """Normalize a notebook text field."""
    return "".join(value) if isinstance(value, list) else value


def _render_output(output: dict[str, Any]) -> str | None:
    """Render a saved text output, ignoring unsupported rich output."""
    if output.get("output_type") == "stream":
        return _text(output.get("text", ""))

    plain_text = output.get("data", {}).get("text/plain")
    if plain_text is not None:
        return _text(plain_text)

    if output.get("output_type") == "error":
        return "\n".join(output.get("traceback", ()))

    return None


def _render_notebook() -> str:
    """Convert the canonical notebook's Markdown, code, and saved outputs."""
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    source_note = (
        '!!! info "Complete workflow"\n\n'
        "    This notebook is the end-to-end example: it locates the CIViC "
        "files, checks compatibility, loads two buns, inspects collections, "
        "works with typed GKM objects, follows references, and compares "
        "assertions. The other Python pages are focused guides to individual "
        "capabilities.\n\n"
        f"    Rendered from `{NOTEBOOK.as_posix()}`."
    )
    rendered: list[str] = []
    first_markdown_cell = True

    for cell in notebook["cells"]:
        source = _text(cell.get("source", "")).rstrip()
        if cell["cell_type"] == "markdown":
            if first_markdown_cell:
                heading, separator, body = source.partition("\n")
                rendered.extend((heading, source_note, body if separator else ""))
                first_markdown_cell = False
            else:
                rendered.append(source)
            continue

        if cell["cell_type"] != "code":
            continue

        execution_count = cell.get("execution_count")
        title = f' title="In [{execution_count}]"' if execution_count else ""
        rendered.append(f"````python{title}\n{source}\n````")

        outputs = filter(
            None, (_render_output(item) for item in cell.get("outputs", ()))
        )
        rendered.extend(
            f"**Output:**\n\n````text\n{output.rstrip()}\n````" for output in outputs
        )

    return "\n\n".join(rendered) + "\n"


with mkdocs_gen_files.open(NOTEBOOK_PAGE, "w") as output:
    output.write(_render_notebook())

for example_path in discover_example_paths():
    with mkdocs_gen_files.open(BUNDLE_OUTPUT_DIR / example_path.name, "wb") as output:
        output.write(example_path.read_bytes())
