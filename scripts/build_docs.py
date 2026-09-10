"""Stage source and generated documentation for a Zensical build."""

from pathlib import Path
from shutil import copytree, rmtree

from scripts.gen_downloads import main as generate_downloads
from scripts.gen_filter_pages import main as generate_filter_pages
from scripts.gen_notebook_files import main as generate_notebook_files
from scripts.gen_schema_pages import main as generate_schema_pages
from scripts.gen_supported_versions import main as generate_supported_versions

SOURCE_DIR = Path("docs")
OUTPUT_DIR = Path("docs-build")
EXCLUDED_PATHS = {
    Path("superpowers"),
    Path("user-stories/_template"),
    Path("user-stories/patterns.yml"),
}


def _ignore(directory: str, names: list[str]) -> set[str]:
    directory_path = Path(directory)
    relative_directory = directory_path.relative_to(SOURCE_DIR)
    return {name for name in names if relative_directory / name in EXCLUDED_PATHS}


def main() -> None:
    """Create a clean staged tree and add all generated documentation."""
    if OUTPUT_DIR.exists():
        rmtree(OUTPUT_DIR)
    copytree(SOURCE_DIR, OUTPUT_DIR, ignore=_ignore)
    generate_filter_pages(OUTPUT_DIR)
    generate_notebook_files(OUTPUT_DIR)
    generate_schema_pages(OUTPUT_DIR)
    generate_supported_versions(OUTPUT_DIR)
    generate_downloads(OUTPUT_DIR)


if __name__ == "__main__":
    main()
