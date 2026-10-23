# Bundle examples

These examples are **small, focused subsets of a producer's actual published
dataset**. They let readers inspect genuine, unmodified GKM records without
downloading the full dataset.

!!! note "Want the full dataset?"

    Download a producer's complete dataset from the [Public bundle repository](repository.md).

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

This ClinVar-GKM bundle example shows one submitter's complete footprint in
ClinVar. It uses the ClinVar-GKM 1.1.0
[`clinvar-gkm-bundle.schema.json`](https://raw.githubusercontent.com/clingen-data-model/clinvar-gkm/1.1.0/schema/clinvar-gkm/clinvar-gkm-bundle.schema.json){ target="_blank" rel="noopener" }
bundle schema.

!!! warning "Snapshot of the 2026-10-18 ClinVar release"

    This example was extracted from the ClinVar-GKM build of the **2026-10-18**
    ClinVar weekly release and is not updated. Later ClinVar releases may add,
    update, or remove these submissions. For current data, download the latest
    `clinvar-gkm` bundle from the [Public bundle repository](repository.md).

The file is a complete, connected subset of that release. It is gzip-compressed
(1.6 MB; 43 MB uncompressed). Download and decompress it to inspect the records
and bundle-local references.

- [**`nch-igm-bundle.json.gz`**](https://raw.githubusercontent.com/clingen-data-model/clinvar-gkm/796a3a8c34e85a75d33a94451373b11645b9ec20/nch-igm-bundle.json.gz)
  represents every ClinVar submission from the
  [IGM Clinical Laboratory at Nationwide Children's Hospital](https://www.ncbi.nlm.nih.gov/clinvar/submitters/196472/)
  (submitter `196472`) as of 2026-10-18: all 2,443 of its submitted clinical variant
  classifications (SCVs), together with the variations, conditions, propositions,
  and evidence lines they reference. It was extracted with the ClinVar-GKM
  [sub-bundle tool](https://dataexchange.clinicalgenome.org/clinvar-gkm/pipeline/sub-bundle/){ target="_blank" rel="noopener" }.
