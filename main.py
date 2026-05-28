"""mkdocs-macros entrypoint for the GKS Starter Kit.

Registers a `list_vignettes` macro used by docs/vignettes/index.md to render
the catalog. All real work is in scripts/vignette_loader.
"""

import sys
from pathlib import Path

# mkdocs-macros loads this file via spec.loader.exec_module, which doesn't add
# the project root to sys.path. Insert it so `from scripts...` imports resolve.
_PROJECT_ROOT = str(Path(__file__).resolve().parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from scripts.vignette_loader import load_vignettes  # noqa: E402


def define_env(env):
    """Hook called by mkdocs-macros-plugin during site build."""
    env.macro(load_vignettes, "list_vignettes")
