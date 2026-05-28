"""mkdocs-macros entrypoint for the GKS Starter Kit.

Registers a `list_vignettes` macro used by docs/vignettes/index.md to render
the catalog. All real work is in scripts/vignette_loader.
"""

from .vignette_loader import load_vignettes


def define_env(env):
    """Hook called by mkdocs-macros-plugin during site build."""
    env.macro(load_vignettes, "list_vignettes")
