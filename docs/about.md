# About

## What is GKS?

The **GA4GH Genomic Knowledge Standards (GKS)** are a set of open community standards for describing, exchanging, and reasoning over genomic knowledge — variants, the categories they fall into, and the clinical or research evidence attached to them. They give knowledgebases, registries, labs, and tool builders a shared way to talk about the same biology, so that data flows cleanly between systems instead of getting stuck in translation.

## What this Starter Kit is (and isn't)

The GKS reference libraries let you *create* and *validate* genomic knowledge objects. But they say nothing about the layer that comes next: how you **collect** that knowledge, make it **interoperable** across resources, **share** it, and **consume** it. The **GKS Starter Kit** is the single community-facing entry point that demonstrates this missing layer.

It does so through three pillars:

1. **[Data Bundles](data/index.md)** — real content from community partners, composed from the modular GKS schemas into larger, shareable bundle documents. This is the *collect, make interoperable, and share* part.
2. **[Python Package](library/index.md)** — a lightweight layer on top of the reference libraries that loads bundles into in-memory GKS objects, lets you explore and manipulate them, and exports back to GKS JSON. This is the *consume and build with* part.
3. **[Vignettes](vignettes/index.md)** — real community use cases that show what a group needs the standards for, and the standards delivering it. Some build on the first two pillars; some do not.

It is *not* a per-product tutorial. Each GKS product has its own **Quick Start Guide** on its own documentation site — those are the right place to learn how to *produce* data in a specific GKS format. The Starter Kit is the layer above: ecosystem orientation, live implementations, and shared adoption patterns. (Only this GKS-level resource is a "Starter Kit"; the per-product guides are Quick Start Guides.)

## Where else to look

- **[GA4GH Starter Kit](https://starterkit.ga4gh.org/)** — the broader GA4GH ecosystem entry point, of which the GKS Starter Kit is a sibling.
- **GKS product documentation:**
    - [VRS — Variation Representation Specification](https://vrs.ga4gh.org/)
    - [Cat-VRS — Categorical Variation Representation](https://cat-vrs.ga4gh.org/)
    - [VA-Spec — Variant Annotation Specification](https://va-ga4gh.readthedocs.io/)
- **GKS Home Page** — coming soon; will reference vignettes from this Starter Kit.
- **[GA4GH Genomic Knowledge Standards](https://www.ga4gh.org/work_stream/genomic-knowledge-standards/)** — Work Stream overview.
