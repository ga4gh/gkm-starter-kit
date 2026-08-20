"""Discover bundle examples and render their documentation links."""

from __future__ import annotations

from pathlib import Path

BUNDLE_SOURCE_DIR = Path("notebooks/civic/bundles")
BUNDLE_OUTPUT_DIR = Path("data/bundles")


def discover_bundle_paths() -> tuple[Path, ...]:
    """Return repository example bundle files in name order."""
    return tuple(sorted(BUNDLE_SOURCE_DIR.glob("*-bundle.json")))


def discover_example_paths() -> tuple[Path, ...]:
    """Return bundle and producer-schema files used by repository examples."""
    paths = {*discover_bundle_paths(), *BUNDLE_SOURCE_DIR.glob("*.schema.json")}
    return tuple(sorted(paths))


def render_bundle_links(base_path: str = "bundles") -> str:
    """Render direct links derived from the repository example bundles."""
    rendered: list[str] = []

    for path in discover_bundle_paths():
        target = Path(base_path) / path.name
        rendered.append(
            f"- [**`{path.name}`**]({target.as_posix()})"
            f'{{ target="_blank" rel="noopener" }}'
        )

    return "\n".join(rendered)


def render_bundle_linkouts(base_path: str, *filenames: str) -> str:
    """Render compact inline links to selected repository example files."""
    paths = discover_example_paths()
    if filenames:
        selected = set(filenames)
        paths = tuple(path for path in paths if path.name in selected)
        missing = selected.difference(path.name for path in paths)
        if missing:
            message = f"Unknown example files: {', '.join(sorted(missing))}"
            raise ValueError(message)

    return " · ".join(
        f"[`{path.name}`]({(Path(base_path) / path.name).as_posix()})"
        f'{{ target="_blank" rel="noopener" }}'
        for path in paths
    )
