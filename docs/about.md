---
hide:
  - navigation
---

# Genomic Knowledge Model

The **Genomic Knowledge Model (GKM)** defines shared models for genomic
variation and related knowledge. It is part of the broader [GA4GH Genomic
Knowledge Standards (GKS)](https://www.ga4gh.org/work_stream/genomic-knowledge-standards/)
Work Stream.

## Standards

GKM brings together four complementary standards, each covering a different part
of genomic knowledge. The standards are layered, starting with shared concepts
and building toward more specific kinds of genomic knowledge.

<div class="gks-standard-stack" aria-label="GKS-Core is the foundation, with VRS, Cat-VRS, and VA-Spec building on it">
  <div class="gks-standard-layer gks-standard-layer--va-spec">
    <a class="gks-standard-block" href="https://va-ga4gh.readthedocs.io/">
      <strong>VA-Spec</strong>
      <span>Use for statements, assertions, and their supporting evidence.</span>
    </a>
  </div>
  <div class="gks-standard-layer gks-standard-layer--cat-vrs">
    <a class="gks-standard-block" href="https://cat-vrs.ga4gh.org/">
      <strong>Cat-VRS</strong>
      <span>Use for categories of variation.</span>
    </a>
  </div>
  <div class="gks-standard-layer gks-standard-layer--vrs">
    <a class="gks-standard-block" href="https://vrs.ga4gh.org/">
      <strong>VRS</strong>
      <span>Use for precise molecular variation.</span>
    </a>
  </div>
  <div class="gks-standard-layer gks-standard-layer--core">
    <a class="gks-standard-block" href="https://github.com/ga4gh/gkm-core">
      <strong>GKS-Core</strong>
      <span>Use for concepts shared across genomic knowledge.</span>
    </a>
  </div>
</div>

The standards can be used independently or combined, so implementers can adopt
only the models their knowledge requires. For example, a resource that
exchanges precise variants may need only VRS, while one that groups variants or
makes evidence-backed assertions can combine VRS with Cat-VRS, VA-Spec, or
both.
