# Public bundle repository

The public bundle repository provides access to **complete, published GKM
bundles** and their schemas. Each bundle contains the dataset its producer
releases for that version. For small, focused subsets of a producer's actual
data, see the [bundle examples](examples.md).

## Downloads

Download the files below. The table is generated during the documentation build.

{{ downloads_table }}

## Resources

### CIViC

The `civic` bundle is hosted in the repository index. Access it programmatically
through the [Python API](../../tools/gkm-toolkit/api/repository.md) using
`BundleRepository`.

### ClinVar-GKM

The `clinvar-gkm` bundle is hosted on the ClinVar-GKM download site, which is
updated with each weekly ClinVar release. Its **Bundle** link always downloads
the latest weekly full bundle.

ClinVar-GKM also publishes monthly and historical full bundles, weekly deltas,
and Parquet files. For these releases and their documentation, see the
[ClinVar-GKM downloads](https://dataexchange.clinicalgenome.org/clinvar-gkm/data-access/download/).

!!! note "Programmatic access"

    `clinvar-gkm` is not yet listed in the repository index, so `BundleRepository`
    cannot load it. Download it from the link above.

!!! info "Dataset contributions"

    Support for contributing additional datasets to the public repository is planned. Contribution guidance will be published when the hosting and review process is ready.
