# About

The GKM Starter Kit is a community project for sharing and using genomic
knowledge represented with the Genomic Knowledge Model.

## What is GKM?

The **Genomic Knowledge Model (GKM)** defines shared models for genomic
variation and related knowledge. It is part of the broader [GA4GH Genomic
Knowledge Standards (GKS)](https://www.ga4gh.org/work_stream/genomic-knowledge-standards/)
family.

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

The Starter Kit builds on GKM through three pillars:

1. **[Data Bundles](data/index.md)** package real GKM data from community
   partners for others to use.
2. **[Python Package](library/index.md)** loads, explores, and writes bundles
   while preserving each producer's names and organization.
3. **[Vignettes](vignettes/index.md)** show how communities put GKM standards
   to work on real problems.

!!! important "Bundles are optional in GKM"

    A GKM bundle is a producer-defined JSON document that packages related GKM
    objects. Bundles are not required to use GKM: applications can work with
    individual objects through the reference implementations above, and
    services can expose their own APIs. Bundles are, however, the input and
    output format of the Starter Kit Python package.

Next, read [Why GKM and the Starter Kit matter](why.md).
