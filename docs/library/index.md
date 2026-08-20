# Python Package

![GKM Starter Kit Logo](../assets/images/gkm-starter-kit-logo.png){: width="300" style="display: block; margin: 0 auto;"}

The [**Genomic Knowledge Model (GKM)**](../about.md#what-is-gkm) gives genomic
knowledge a shared structure and meaning. GKM standards can also be used
directly through their reference implementations or exposed through service
APIs; GKM itself does not require bundles. The Starter Kit package does: it is
for consumers who want to load a producer's GKM Bundle, explore its contents in
Python, follow relationships, and write it back to JSON.

GA4GH reference implementations handle GKM objects; the Starter Kit handles
the producer-defined bundle around them. The Python API represents a loaded
GKM bundle with the `Bundle` class.

## Install

The package requires Python 3.11 or later. Install it from PyPI:

```shell
python3 -m pip install gkm.starter
```

Import the public interface through `gkm.starter`:

```python
from gkm import starter
```

## What the package adds

The package provides a consistent way to read producer JSON, construct GKM
objects, and follow relationships while preserving the producer's format.

Consumers can discover a bundle's contents, use supported GKM Python models,
and follow links. Producers keep their own organization while making their
data accessible through the same tools.

For the broader producer and consumer benefits, see [Why use GKM and the
Starter Kit?](../why.md).

A **collection** maps object identifiers to objects within a bundle. Producers
choose collection names, and the Starter Kit exposes those same names in
Python. Someone familiar with the source data can navigate the bundle using
familiar terms instead of learning Starter Kit names for every collection.

## What you can do

- Load producer JSON with its producer-defined schema.
- Discover the collections provided by a producer.
- Work with supported values as GKM Python models.
- Follow relationships between objects without manually navigating JSON paths.
- Write the bundle back to JSON while preserving producer-specific content.

!!! note "In development"

    You can load, explore, and write bundles now. Full JSON Schema validation
    and automatic linking between referenced objects are still in development.

## Guided notebook

The CIViC notebook walks through the complete process. It registers and loads
two bundles, inspects their contents, follows references, and compares VA-Spec
assertion models.

The pages below explain individual behaviors, boundaries, and failure modes.
Use the notebook to see them work together on real data.

[**View the notebook ↗**](civic-notebook.md){ target="_blank" rel="noopener" }

## Learn more

- [Loading a bundle](loading.md) — accepted inputs, schema use, and compatibility.
- [Working with bundles](exploring.md) — collections, GA4GH reference models, and
  local references.
- [Saving and exporting a bundle](writing.md) — dictionaries, JSON output, and
  current fidelity guarantees.
- [Bundle formats and JSON Schema](../data/formats.md) — required
  format rules and versioning guidance for producers.
- [API reference](api/index.md) — public functions, types, methods, and exceptions.
