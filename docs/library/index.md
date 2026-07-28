# Python Package

The GKS reference libraries — [`vrs-python`](https://github.com/ga4gh/vrs-python),
`cat-vrs-python`, and `va-spec-python` — give you validated building blocks for
individual GKS objects. What they don't give you is a way to work with a whole
**[Data Bundle](../data/index.md)** as one thing. The Python package is that
missing layer: a lightweight wrapper on top of the reference libraries that
lets you **load** a bundle into in-memory GKS objects, **explore** and
manipulate those objects with ordinary Python, and **export** them back to
canonical GKS JSON.

The intent is deliberately thin. The package does not reinvent variant
normalization or statement validation — it delegates that to the reference
libraries — it simply makes a bundle pleasant to open, walk, change, and write
back out without hand-parsing JSON.

!!! note "In development"

    This package is in active design. The load / explore / export shape shown
    below is the intended developer experience, not a released API. A
    forthcoming Pillar 2 specification and implementation plan will define the
    object model, the loaders, and the exporters; this page will link to it
    once it lands.

## The intended experience

The three moves below are the whole point of the package: get a bundle in,
work with it, get valid GKS back out.

=== "Load"

    ```python
    from gks_kit import load                    # package name TBD

    bundle = load("clinvar.gks.json")           # parse + validate against the bundle schema
    ```

=== "Explore"

    ```python
    for stmt in bundle.statements:
        print(stmt.proposition.predicate, "→", stmt.proposition.object["label"])
        # isCausalFor → hereditary breast-ovarian cancer syndrome

    stmt = bundle.statements[0]
    stmt.direction                              # 'supports'
    ```

=== "Export"

    ```python
    bundle.to_json("out.gks.json")              # canonical GKS JSON, re-validated on write
    ```

!!! info "`gks_kit` is a placeholder"

    The import name `gks_kit` used throughout this page is a stand-in. The
    final package name has not been decided, so treat every `gks_kit` here as
    "the package, whatever it ends up being called."

## Extending propositions

GKS prescribes a set of specialized propositions — for example
`VariantPathogenicityProposition` — that cover the most common assertions. When
a resource needs to make a statement about a proposition GKS does not
prescribe, the planned pathway is **`CustomProposition`**: a forthcoming
va-spec escape hatch that lets a bundle carry a well-formed statement over a
proposition shape the core specs don't yet define, without dropping out of the
GKS model. `CustomProposition` is not yet specified — this names the intended
direction only; its schema and validation rules will be defined in their own
spec.
