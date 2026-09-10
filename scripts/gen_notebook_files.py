"""Publish and render notebooks in the documentation site."""

import json
from pathlib import Path
from typing import Any

from scripts.bundle_examples import (
    BUNDLE_OUTPUT_DIR,
    discover_example_paths,
    render_bundle_linkouts,
)

SOURCE_DIR = Path("notebooks/civic")
NOTEBOOK = SOURCE_DIR / "explore-civic-bundles.ipynb"
NOTEBOOK_PAGE = Path("toolkit/notebooks/civic-notebook.md")
REPOSITORY_NOTEBOOK = Path("notebooks/repository/load-public-bundle.ipynb")
REPOSITORY_NOTEBOOK_PAGE = Path("toolkit/notebooks/repository-notebook.md")


def _text(value: str | list[str]) -> str:
    """Normalize a notebook text field."""
    return "".join(value) if isinstance(value, list) else value


def _render_output(output: dict[str, Any]) -> tuple[str, str | None] | None:
    """Return supported output text and its Markdown code-fence language."""
    if output.get("output_type") == "stream":
        text = _text(output.get("text", ""))
        try:
            json.loads(text)
        except json.JSONDecodeError:
            return text, "text"
        return text, "json"

    json_value = output.get("data", {}).get("application/json")
    if json_value is not None:
        return json.dumps(json_value, indent=2), "json"

    markdown = output.get("data", {}).get("text/markdown")
    if markdown is not None:
        return _text(markdown), None

    plain_text = output.get("data", {}).get("text/plain")
    if plain_text is not None:
        text = _text(plain_text)
        if "text/html" in output.get("data", {}):
            try:
                json.loads(text)
            except json.JSONDecodeError:
                pass
            else:
                return text, "json"
        return text, "python"

    if output.get("output_type") == "error":
        return "\n".join(output.get("traceback", ())), "text"

    return None


def _render_notebook(notebook_path: Path, source_note: str = "") -> str:
    """Convert a notebook's Markdown, code, and saved outputs."""
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    source_note = source_note or (
        f'!!! info "Notebook source"\n\n    Rendered from `{notebook_path.as_posix()}`.'
    )
    civic_source_note = (
        '!!! info "Data files"\n\n'
        "    Example files: "
        + render_bundle_linkouts(
            "../../data/bundles",
            "civic-assertion-9-bundle.json",
            "civic-assertion-251-bundle.json",
            "civic-gks-bundle-v0.1.0.schema.json",
        )
        + "\n\n"
        f"    Rendered from `{notebook_path.as_posix()}`."
    )
    rendered: list[str] = []
    first_markdown_cell = True

    for cell in notebook["cells"]:
        source = _text(cell.get("source", "")).rstrip()
        if cell["cell_type"] == "markdown":
            if first_markdown_cell:
                heading, separator, body = source.partition("\n")
                rendered.extend(
                    (
                        heading,
                        civic_source_note if notebook_path == NOTEBOOK else source_note,
                        body if separator else "",
                    )
                )
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
        for output, language in outputs:
            if language is None:
                rendered.append(f"**Output:**\n\n{output.rstrip()}")
            else:
                rendered.append(
                    f"**Output:**\n\n````{language}\n{output.rstrip()}\n````"
                )

    return "\n\n".join(rendered) + "\n"


def main(output_root: Path = Path("docs")) -> None:
    """Render the notebook and copy its downloadable data into the docs tree."""
    for source_path, output_path in (
        (NOTEBOOK, NOTEBOOK_PAGE),
        (REPOSITORY_NOTEBOOK, REPOSITORY_NOTEBOOK_PAGE),
    ):
        notebook_path = output_root / output_path
        notebook_path.parent.mkdir(parents=True, exist_ok=True)
        notebook_path.write_text(_render_notebook(source_path), encoding="utf-8")

    bundle_dir = output_root / BUNDLE_OUTPUT_DIR
    bundle_dir.mkdir(parents=True, exist_ok=True)
    for example_path in discover_example_paths():
        (bundle_dir / example_path.name).write_bytes(example_path.read_bytes())
