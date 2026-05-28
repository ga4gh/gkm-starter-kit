"""GKS Starter Kit build scripts.

Re-exports `define_env` so mkdocs-macros can load this package via
`module_name: scripts` in mkdocs.yml.
"""

from .main import define_env

__all__ = ["define_env"]
