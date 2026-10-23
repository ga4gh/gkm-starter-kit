# Bundle examples

These examples are **small, focused subsets of a producer's actual published
dataset**. They let readers inspect genuine, unmodified GKM records without
downloading the full dataset.

!!! note "Want the full dataset?"

    Download a producer's complete dataset from the [Public bundle repository](repository.md),
    or from the producer's own download site for very large datasets such as ClinVar-GKM.

## CIViC

These two CIViC bundle examples show different VA-Spec assertion types. Both use
the [`civic-gkm-bundle-v0.1.0-a0.schema.json`](civic-gkm-bundle-v0.1.0-a0.schema.json){ target="_blank" rel="noopener" }
bundle schema.

Each file is a complete, connected subset of CIViC data. Open it to inspect the
records and bundle-local references.

- [**`civic-assertion-9-bundle.json`**](civic-assertion-9-bundle.json){ target="_blank" rel="noopener" }
  represents [CIViC Assertion 9](https://civicdb.org/links/assertion/9): a Tier II
  clinical-significance assertion under the AMP/ASCO/CAP Guidelines (2017), together
  with its diagnostic propositions and evidence.
- [**`civic-assertion-251-bundle.json`**](civic-assertion-251-bundle.json){ target="_blank" rel="noopener" }
  represents [CIViC Assertion 251](https://civicdb.org/links/assertion/251): a
  likely-oncogenic assertion under the ClinGen/CGC/VICC Guidelines for Oncogenicity
  (2022).

## ClinVar-GKM

This ClinVar-GKM bundle example shows everything ClinVar holds about one
variation. It uses the ClinVar-GKM 1.1.0
[`clinvar-gkm-bundle-1.1.0.schema.json`](clinvar-gkm-bundle-1.1.0.schema.json){ target="_blank" rel="noopener" }
bundle schema.

!!! warning "Snapshot of the 2026-10-18 ClinVar release"

    This example was extracted from the ClinVar-GKM build of the **2026-10-18**
    ClinVar weekly release and is not updated. Later ClinVar releases may add,
    update, or remove these records. For current data, use the complete
    ClinVar-GKM releases on the
    [ClinVar-GKM download site](https://dataexchange.clinicalgenome.org/clinvar-gkm/data-access/download/).

The file is a complete, connected subset of that release. Open it to inspect the
records and bundle-local references.

- [**`clinvar-variation-10-bundle.json`**](clinvar-variation-10-bundle.json){ target="_blank" rel="noopener" }
  represents [ClinVar Variation 10](https://www.ncbi.nlm.nih.gov/clinvar/variation/10/),
  `NM_000410.4(HFE):c.187C>G (p.His63Asp)`, as of 2026-10-18. It includes all
  61 submitted classifications (SCVs), the 30 condition-level (RCV) and 10
  variation-level (VCV) aggregate statements, and every variation, condition,
  proposition, evidence line, and submitter record they reference. The
  aggregate statements show several kinds of ClinVar classification for one
  variant: conflicting classifications of pathogenicity, risk factor, other, and
  not provided. It was extracted with the ClinVar-GKM
  [sub-bundle tool](https://dataexchange.clinicalgenome.org/clinvar-gkm/pipeline/sub-bundle/){ target="_blank" rel="noopener" }.
