"""Publish and render notebooks in the documentation site."""

import json
from pathlib import Path

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
    return "".join(value) if isinstance(value, list) else value


def _render_notebook(path: Path) -> str:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    note = f'!!! info "Notebook source"\n\n    Rendered from `{path.as_posix()}`.'
    if path == NOTEBOOK:
        note = (
            '!!! info "Data files"\n\n    Example files: '
            + render_bundle_linkouts(
                "../../data/bundles",
                "civic-assertion-9-bundle.json",
                "civic-assertion-251-bundle.json",
                "civic-gks-bundle-v0.1.0.schema.json",
            )
            + f"\n\n    Rendered from `{path.as_posix()}`."
        )
    rendered = []
    first = True
    for cell in notebook["cells"]:
        source = _text(cell.get("source", "")).rstrip()
        if cell["cell_type"] == "markdown":
            if first:
                heading, separator, body = source.partition("\n")
                rendered += [heading, note, body if separator else ""]
                first = False
            else:
                rendered.append(source)
        elif cell["cell_type"] == "code":
            count = cell.get("execution_count")
            title = f' title="In [{count}]"' if count else ""
            rendered.append(f"````python{title}\n{source}\n````")
    return "\n\n".join(rendered) + "\n"


def main(output_root: Path = Path("docs")) -> None:
    """Render notebooks and copy their downloadable data into staged docs."""
    for source, target in (
        (NOTEBOOK, NOTEBOOK_PAGE),
        (REPOSITORY_NOTEBOOK, REPOSITORY_NOTEBOOK_PAGE),
    ):
        target_path = output_root / target
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(_render_notebook(source), encoding="utf-8")
    bundle_dir = output_root / BUNDLE_OUTPUT_DIR
    bundle_dir.mkdir(parents=True, exist_ok=True)
    for example_path in discover_example_paths():
        (bundle_dir / example_path.name).write_bytes(example_path.read_bytes())
