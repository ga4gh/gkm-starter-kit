"""mkdocs-macros entrypoint for the GKS Starter Kit.

Registers a `list_vignettes` macro used by docs/vignettes/index.md to render
the catalog. All real work is in scripts/vignette_loader.
"""

from collections.abc import Callable
from typing import Protocol

from .bundle_examples import render_bundle_linkouts, render_bundle_links
from .vignette_loader import load_patterns, load_vignettes


class MacroEnvironment(Protocol):
    """Provide the macro registration interface used by this module."""

    def macro(self, func: Callable[..., object], name: str) -> None:
        """Register a callable as a named macro."""


def define_env(env: MacroEnvironment) -> None:
    """Register macros used during the MkDocs site build."""
    env.macro(load_vignettes, "list_vignettes")
    env.macro(load_patterns, "pattern_labels")
    env.macro(render_bundle_links, "bundle_links")
    env.macro(render_bundle_linkouts, "bundle_linkouts")
