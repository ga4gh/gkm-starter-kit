# Public bundle repository

The public bundle repository provides access to **complete, published GKM
bundles** and their schemas. Each bundle contains the dataset its producer
releases for that version. For small, focused subsets of a producer's actual
data, see the [bundle examples](examples.md).

## Downloads

### Public repository

Download the files below, or access them programmatically through the
[Python API](../../tools/gkm-toolkit/api/repository.md). This table lists datasets
available through `BundleRepository` and is generated during the documentation
build.

{{ downloads_table }}

!!! info "Dataset contributions"

    Support for contributing additional datasets to the public repository is planned. Contribution guidance will be published when the hosting and review process is ready.

### Implementer-hosted data

These datasets are hosted by their implementers and are not currently available
through `BundleRepository` or its Python API. Follow each site's instructions to
download and use the data. Support for accessing implementer-hosted datasets is
planned for future versions of the toolkit.

| Resource | Description | Download site |
| --- | --- | --- |
| ClinVar-GKM | ClinVar variation and clinical interpretation data represented with GKM standards. In addition to bundles, the official download site provides monthly full releases, weekly deltas, and typed Parquet files, with instructions for downloading and querying the data. | [Explore ClinVar-GKM downloads](https://dataexchange.clinicalgenome.org/clinvar-gkm/data-access/download/) |
