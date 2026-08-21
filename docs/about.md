# About the GKM Starter Kit

The GKM Starter Kit is a community project for sharing and using genomic
knowledge represented with the Genomic Knowledge Model.

## What is GKM?

The **Genomic Knowledge Model (GKM)** defines shared models for genomic
variation and related knowledge. It is part of the broader [GA4GH Genomic
Knowledge Standards (GKS)](https://www.ga4gh.org/work_stream/genomic-knowledge-standards/)
Work Stream.

GKM brings together four standards that can be used independently or combined:

- **[GKS-Core](https://github.com/ga4gh/gks-core)** provides concepts shared by
  the other standards.
- **[VRS](https://vrs.ga4gh.org/)** describes precise molecular variation.
- **[Cat-VRS](https://cat-vrs.ga4gh.org/)** describes categories of variation.
- **[VA-Spec](https://va-ga4gh.readthedocs.io/)** describes what is known or
  asserted about variation, including supporting evidence.

Producers use the standards that fit their data. Their Python reference
implementations are:

- **GKS-Core and VRS:** [vrs-python](https://github.com/ga4gh/vrs-python)
- **Cat-VRS:** [cat-vrs-python](https://github.com/ga4gh/cat-vrs-python)
- **VA-Spec:** [va-spec-python](https://github.com/ga4gh/va-spec-python)

## The three pillars

The Starter Kit connects GKM standards to real data, software, and community
outcomes through three pillars.

### Data Bundles

**[Data Bundles](data/index.md) package related GKM objects while preserving the
names and organization of their resources.**

A documented, versioned bundle schema makes structural changes easier to
communicate and helps consumers understand what a producer distributes.

!!! important "Bundles are optional in GKM"

    A GKM bundle packages related GKM objects using a producer-defined
    structure. Bundles are not required to use GKM: applications can construct,
    validate, and serialize individual GKM objects through the reference
    implementations above.

### The `gkm.starter` Python package

**[`gkm.starter`](library/index.md) provides a consistent Python interface for
loading, exploring, and writing bundles.**

Consumers can work with supported GKM Python models, follow relationships
between objects, and retain producer-specific content without hand-parsing each
producer's organization.

Bundles are the input and output format of `gkm.starter`. The initial
implementation supports JSON serialization; other serializations may be added
later.

The GKM reference implementations construct, validate, and serialize individual
GKM objects; `gkm.starter` works with collections of those objects in bundles.
These packages are maintained implementations, not required interfaces.
Developers can implement the GKM standards in their own tools and programming
languages.

### Vignettes

**[Vignettes](vignettes/index.md) show how communities put GKM standards to work
and what their implementations accomplish.**

They give prospective adopters concrete examples, reveal reusable patterns,
and help teams evaluate whether GKM fits their needs.

Some vignettes use Data Bundles or `gkm.starter`; others use GKM standards
without them. The focus is the real-world outcome, not whether an implementation
uses every part of the Starter Kit.

## How the pillars work together

Data Bundles provide real data, `gkm.starter` provides a consistent bundle
workflow, and Vignettes demonstrate the results. Together they help producers,
consumers, and the GKM community test the standards, identify gaps, and turn
successful implementations into patterns others can reuse.
