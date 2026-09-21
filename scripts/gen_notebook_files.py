"""Publish and render notebooks in the documentation site."""

import json
from pathlib import Path
from typing import Any

from scripts.bundle_examples import (
    BUNDLE_OUTPUT_DIR,
    discover_example_paths,
    render_bundle_linkouts,
)

NOTEBOOK = Path("notebooks/civic/bundles/explore-civic-bundles.ipynb")
NOTEBOOK_PAGE = Path("tools/gkm-toolkit/notebooks/civic-notebook.md")
ONCOGENICITY_DIR = Path("notebooks/civic/vignettes/oncogenicity")
ONCOGENICITY_NOTEBOOK = ONCOGENICITY_DIR / "civic-oncogenicity-gkm.ipynb"
ONCOGENICITY_NOTEBOOK_PAGE = Path(
    "user-stories/civic/civic-oncogenicity-gkm/notebook.md"
)
REPOSITORY_NOTEBOOK = Path("notebooks/repository/load-public-bundle.ipynb")
REPOSITORY_NOTEBOOK_PAGE = Path("tools/gkm-toolkit/notebooks/repository-notebook.md")


def _text(value: str | list[str]) -> str:
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

    data = output.get("data", {})
    json_value = data.get("application/json")
    if json_value is not None:
        return json.dumps(json_value, indent=2), "json"

    markdown = data.get("text/markdown")
    if markdown is not None:
        return _text(markdown), None

    plain_text = data.get("text/plain")
    if plain_text is not None:
        text = _text(plain_text)
        if "text/html" in data:
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


def _render_notebook(path: Path) -> str:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    note = f'!!! info "Notebook source"\n\n    Rendered from `{path.as_posix()}`.'
    if path == NOTEBOOK:
        note = (
            '!!! info "Data files"\n\n    Example files: '
            + render_bundle_linkouts(
                "../../../data/bundles",
                "civic-assertion-9-bundle.json",
                "civic-assertion-251-bundle.json",
                "civic-gks-bundle-v0.1.0.schema.json",
            )
            + f"\n\n    Rendered from `{path.as_posix()}`."
        )
    elif path == ONCOGENICITY_NOTEBOOK:
        note = f'!!! info "Notebook source"\n\n    Rendered from `{path.as_posix()}`.'
    rendered = []
    first = True
    for cell in notebook["cells"]:
        source = _text(cell.get("source", "")).rstrip()
        if cell["cell_type"] == "markdown":
            if path == ONCOGENICITY_NOTEBOOK:
                source = source.replace(
                    "../../bundles/explore-civic-bundles.ipynb",
                    "../../../tools/gkm-toolkit/notebooks/civic-notebook.md",
                )
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
            for output in filter(
                None, (_render_output(item) for item in cell.get("outputs", []))
            ):
                text, language = output
                if language is None:
                    rendered.append(f"**Output:**\n\n{text.rstrip()}")
                else:
                    rendered.append(
                        f"**Output:**\n\n````{language}\n{text.rstrip()}\n````"
                    )
    return "\n\n".join(rendered) + "\n"


def main(output_root: Path = Path("docs")) -> None:
    """Render notebooks and copy their downloadable data into staged docs."""
    for source, target in (
        (NOTEBOOK, NOTEBOOK_PAGE),
        (ONCOGENICITY_NOTEBOOK, ONCOGENICITY_NOTEBOOK_PAGE),
        (REPOSITORY_NOTEBOOK, REPOSITORY_NOTEBOOK_PAGE),
    ):
        target_path = output_root / target
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(_render_notebook(source), encoding="utf-8")
    oncogenicity_output_dir = output_root / ONCOGENICITY_NOTEBOOK_PAGE.parent
    for image_source in sorted(ONCOGENICITY_DIR.glob("*.png")):
        image_target = oncogenicity_output_dir / image_source.name
        image_target.write_bytes(image_source.read_bytes())
    bundle_dir = output_root / BUNDLE_OUTPUT_DIR
    bundle_dir.mkdir(parents=True, exist_ok=True)
    for example_path in discover_example_paths():
        (bundle_dir / example_path.name).write_bytes(example_path.read_bytes())
