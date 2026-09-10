---
hide:
  - navigation
---

# Genomic Knowledge Model

The **Genomic Knowledge Model (GKM)** defines shared models for genomic
variation and related knowledge. It is part of the broader [GA4GH Genomic
Knowledge Standards (GKS)](https://www.ga4gh.org/work_stream/genomic-knowledge-standards/)
Work Stream.

## Standards and reference implementations

GKM brings together four complementary standards, each covering a different
part of genomic knowledge. Each standard also has a maintained Python reference
implementation for constructing and validating its models.

| If you need to represent… | GA4GH standard | Python reference implementation |
| --- | --- | --- |
| Concepts shared across genomic knowledge | [GKS-Core](https://github.com/ga4gh/gkm-core) | [vrs-python](https://github.com/ga4gh/vrs-python) |
| Precise molecular variation | [VRS](https://vrs.ga4gh.org/) | [vrs-python](https://github.com/ga4gh/vrs-python) |
| Categories of variation | [Cat-VRS](https://cat-vrs.ga4gh.org/) | [cat-vrs-python](https://github.com/ga4gh/cat-vrs-python) |
| Statements, assertions, and their supporting evidence | [VA-Spec](https://va-ga4gh.readthedocs.io/) | [va-spec-python](https://github.com/ga4gh/va-spec-python) |

The standards can be used independently or combined, so implementers can adopt
only the models their knowledge requires. For example, a resource that
exchanges precise variants may need only VRS, while one that groups variants or
makes evidence-backed assertions can combine VRS with Cat-VRS, VA-Spec, or
both.

!!! note "Python reference implementations are optional"

    The Python reference implementations are one way to work with GKM.
    Implementers can use other languages and tools as long as their data
    conforms to the relevant GKM standards.

## GKM Toolkit

The Python reference implementations work with individual GKM objects. The
Starter Kit's [GKM Toolkit](toolkit/index.md) builds on them to help users load,
explore, and exchange collections of those objects.
