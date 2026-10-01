---
title: "Harmonizing ClinVar by VRS identity"
slug: harmonizing-clinvar-by-vrs-identity
summary: "Republishing all of ClinVar in the GKM so every variant carries a VRS identity and every classification is a structured VA-Spec statement, letting you join ClinVar to any VRS-aware dataset by identity."
products:
  - name: VRS
    version: "2.1.1"
  - name: Cat-VRS
    version: "1.1.1"
  - name: VA-Spec
    version: "1.1.0"
  - name: GKM-Core
    version: "1.3.0"
pattern: cross-source-variant-harmonization
implementer: ClinGen
status: production
contributors:
  - lbabb
last_updated: 2026-10-01
---

# Harmonizing ClinVar by VRS identity

**Why this matters**

ClinVar is the largest public collection of expert interpretations linking genetic variants to health conditions, but combining it with other resources has meant reconciling how each one *describes* a variant — different text formats, coordinate systems, and genome versions — even when they mean the exact same change. ClinVar-GKM republishes the entirety of ClinVar in the GA4GH Genomic Knowledge Model, a shared data standard in which every variant carries a computed identifier derived from its underlying sequence change — identical wherever that same change appears — and every classification is a structured record that keeps its evidence and provenance attached. So you can look up a variant's ClinVar classifications by that shared identifier, and line ClinVar up against any other dataset built on the same standard, without translating coordinates.

**At a glance**

- **Implementer:** ClinGen
- **Products:** <span class="gkm-product-label gkm-product-label--vrs">VRS <small>2.1.1</small></span> <span class="gkm-product-label gkm-product-label--cat-vrs">Cat-VRS <small>1.1.1</small></span> <span class="gkm-product-label gkm-product-label--va-spec">VA-Spec <small>1.1.0</small></span> <span class="gkm-product-label gkm-product-label--gkm-core">GKM-Core <small>1.3.0</small></span>
- **Pattern:** Cross-source variant harmonization
- **Tools:** [vrs-python](https://github.com/ga4gh/vrs-python), [va-spec-python](https://github.com/ga4gh/va-spec-python), and the [GKM Toolkit](../../../tools/gkm-toolkit/getting-started.md); the published clinvar-gkm [bundle](https://dataexchange.clinicalgenome.org/clinvar-gkm/data-access/download/)
- **Status:** <span class="gkm-status gkm-status--production">production</span>

---

## The story

A lab or knowledgebase that wants to annotate its variants with ClinVar's classifications has to answer "is *my* variant the *same* variant ClinVar classified?" — a surprisingly hard question when the two sides use different HGVS transcripts, 0- versus 1-based coordinates, or different genome builds. Teams end up maintaining brittle normalization code just to join two tables, and the join silently misses variants whose descriptions don't line up. And once a match is found, ClinVar's flat XML says *what* the classification is but not, in a machine-actionable way, *who* made it, *how*, or *against which method*.

ClinVar-GKM removes both frictions. Each ClinVar variant is represented as a Cat-VRS `CategoricalVariant` over one or more VRS alleles; the VRS allele id (`ga4gh:VA.…`) is a digest of the normalized sequence change, so the *same* change computed from any other source produces the *same* id — the join becomes an equality check, with no coordinate math. Each classification is a VA-Spec `Statement` asserting a `Proposition` (variant → condition) with its strength, review status, submitter `Contribution`s, and citations — the same shape whether it came from a single submitter (SCV), a variant-level aggregate (VCV), or a condition-level aggregate (RCV).

Everything is delivered as a single self-describing bundle of named sections that reference each other by `#/section/id` pointers, so a variant, its classifications, conditions, and submitters are all reachable from one download. The bundle is published as a monthly full plus weekly deltas, tracking ClinVar's own release cadence.

## The data

Take the ClinVar expert-panel call on *BRCA1* `c.68_69del` (a pathogenic frameshift). In the bundle it is a small connected graph — the classification statement points at a proposition, which points at the variant, which resolves down to a VRS allele:

```json
// scv/  — the expert-panel classification statement
{
  "id": "clinvar.submission:SCV004101425.2",
  "type": "Statement",
  "classification": { "name": "Pathogenic", "primaryCoding": { "code": "pathogenic", "system": "ACMG Guidelines, 2015" } },
  "quality": { "conceptType": "Quality", "name": "expert panel" },
  "proposition": "#/varcond-proposition/SCV004101425-PATH",
  "contributions": [ { "contributor": "#/submitter/clinvar.submitter:509268", "activityType": "evaluated", "date": "2024-06-11" } ]
}

// varcond-proposition/  — what it asserts
{ "type": "VariantPathogenicityProposition", "predicate": "isCausalFor",
  "subject": "#/variation/clinvar:17662", "object": "#/condition/clinvar.trait:76328" }

// variation/  → allele/  → the VRS identity you can join on
{ "id": "clinvar:17662", "type": "CategoricalVariant", "members": [ "#/allele/ga4gh:VA.EE08XW4IpzeWhJAwComKOSmsPHTcP-1R" ] }
```

Any dataset that computes the same `ga4gh:VA.EE08XW4IpzeWhJAwComKOSmsPHTcP-1R` allele — a VCF annotation pipeline, gnomAD, another knowledgebase — matches this ClinVar classification exactly, and can then read its strength, review status, submitter, and condition straight from the bundle.

## The tools used

- **[vrs-python](https://github.com/ga4gh/vrs-python)** — compute the VRS allele id for your own variants, to join against clinvar-gkm's `allele` section.
- **[va-spec-python](https://github.com/ga4gh/va-spec-python)** — construct and validate the classification `Statement`s and `Proposition`s as typed Python models.
- **[GKM Toolkit](../../../tools/gkm-toolkit/getting-started.md)** (`ga4gh.gkm`) — load a published bundle, follow `#/…` pointers, and export a connected slice, without writing the resolution yourself.
- **The clinvar-gkm [bundle](https://dataexchange.clinicalgenome.org/clinvar-gkm/data-access/download/)** — the monthly full plus weekly deltas on Cloudflare R2.

## How to reuse this pattern

- **Get the data** — the clinvar-gkm [Downloads guide](https://dataexchange.clinicalgenome.org/clinvar-gkm/data-access/download/).
- **Understand the shape** — [Output Format](https://dataexchange.clinicalgenome.org/clinvar-gkm/output-reference/overview/) and [ID References](https://dataexchange.clinicalgenome.org/clinvar-gkm/output-reference/id-references/).
- Other implementers of `cross-source-variant-harmonization`: see [vignettes filtered by this pattern](../../by-pattern/cross-source-variant-harmonization/index.md).
