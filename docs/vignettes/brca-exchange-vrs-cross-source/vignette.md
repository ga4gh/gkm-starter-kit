---
title: "BRCA Exchange: identifying unique variants across sources with VRS"
slug: brca-exchange-vrs-cross-source
summary: "Using VRS digests to deduplicate BRCA variants pulled from ClinVar, gnomAD, LOVD, and the literature."
products:
  - name: VRS
    version: "2.0"
pattern: cross-source-variant-harmonization
implementer: BRCA Exchange
status: pilot
contributors:
  - lbabb
last_updated: 2026-05-27
---

# BRCA Exchange: identifying unique variants across sources with VRS

**Why this matters**

BRCA Exchange aggregates cancer-risk variants in the BRCA1 and BRCA2 genes from many public sources — ClinVar, gnomAD, LOVD, the published literature, and others. Each source describes the same underlying DNA change differently, which makes it hard to tell which records refer to the same variant. By generating a single shared identifier for each variant directly from its sequence change, the project can confidently deduplicate across sources and present a complete, non-redundant view to clinicians and researchers. The result is fewer missed matches, less manual reconciliation, and faster integration of new sources as they become available.

**At a glance**

- **Who:** BRCA Exchange
- **GKS products used:** VRS 2.0
- **Tools:** `vrs-python` (link below)
- **Status:** pilot

---

## The story

BRCA Exchange's mission is to provide a complete, expert-reviewed view of variation in the BRCA1 and BRCA2 genes — both of which carry well-established risks for breast, ovarian, and other cancers. Doing that well means pulling variant records from every credible source: clinical databases like ClinVar, large population studies like gnomAD, locus-specific databases like LOVD, and the literature.

The hard part isn't pulling the records. It's knowing when two records describe the same underlying variant. Historically, this has meant string matching across HGVS expressions and VCF-style coordinates, both of which have well-known pitfalls: HGVS allows multiple equivalent forms for the same change, and VCF representations depend on choices about left-alignment, reference build, and how indels are described. A variant that looks different across two source feeds often turns out to be the same biology.

The Variation Representation Specification (VRS) addresses this by defining a canonical, content-addressed identifier for each variant. The identifier — the VRS digest — is computed deterministically from the variant's normalized representation. Two records that describe the same underlying change get the same digest, regardless of which source they came from or how they were originally expressed. For BRCA Exchange, this means deduplication becomes an exact-match operation on digests, not a fuzzy string-comparison problem.

The workflow looks like this: pull variants from each source; convert each into a normalized VCF representation against GRCh38; compute the VRS digest for each variant; group records by digest to identify the unique-variant superset; then proceed with annotation and curation on the deduplicated set.

## The data

A single BRCA1 variant, expressed as a VRS 2.0 Allele, looks like this:

```json
--8<-- "docs/vignettes/brca-exchange-vrs-cross-source/payloads/brca1-variant.vrs.json"
```

The `id` field (the digest) is what enables exact-match deduplication: any other source describing the same change against the same reference sequence produces the same `id`.

## The tools used

- **[vrs-python](https://github.com/ga4gh/vrs-python)** — the reference Python implementation for normalizing and digesting variants per the VRS spec. Used to compute the digest at the bottom of the pipeline.
- **GRCh38 reference sequence** — pinned to a specific RefSeq accession (e.g. `NC_000017.11` for chromosome 17, where BRCA1 lives) for reproducible digesting.

## How to reuse this pattern

- [VRS Quick Start Guide](https://vrs.ga4gh.org/) — for producing VRS-format records.
- [vrs-python documentation](https://vrs-python.readthedocs.io/) — installation and API reference.
- Other implementers of `cross-source-variant-harmonization`: see [vignettes filtered by this pattern](../by-pattern/cross-source-variant-harmonization/).
