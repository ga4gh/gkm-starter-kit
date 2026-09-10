# Pillar I: Data

GKM describes one piece of genomic knowledge, such as a variant, a category
of variants, or a clinical assertion, in a consistent way. Real resources
contain many of these objects and need consistent ways to share them.
**This pillar shows how GKM data can be packaged and shared in practice**,
from individual records to compact bundles and larger datasets.

## Ways to share GKM data

The initial implementation supports some sharing patterns today. Others remain
in development or are future directions. The right delivery method depends on
the scale and use case.

<div class="grid cards" markdown>

- **One record at a time**

    <span class="gks-status gks-status--production">Available now</span>

    Share a single GKM object in a message or API response.

- **[Compact bundles](bundles/index.md)**

    <span class="gks-status gks-status--production">Available now</span>

    Package related objects together, keeping **shared representations and
    relationships explicit**.

- **Large-volume datasets**

    <span class="gks-status gks-status--pilot">In development</span>

    Use **bulk-friendly formats** such as JSON Lines, Parquet, or relational
    tables as support develops.

</div>

## Built with community partners

The Starter Kit uses real content developed with resources such as
**[ClinVar GKM](https://dataexchange.clinicalgenome.org/clinvar-gkm/)** and
**CIViC**. Each partner defines its collection names and object
groupings in a bundle schema, preserving familiar terminology while using
shared GKM models.

This section will grow with the community's needs.
