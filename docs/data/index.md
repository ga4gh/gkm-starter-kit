# Pillar I: Data

GKM describes one piece of genomic knowledge, such as a variant, a category
of variants, or a clinical assertion, in a consistent way. Real resources
contain many of these objects and need consistent ways to share them.
**This pillar shows how GKM data can be packaged and shared in practice**,
from individual records to compact bundles and larger datasets.

## Ways to share GKM data

The right delivery method depends on the scale and the use case. The initial
implementation supports some patterns today; others are in development.

<div class="grid cards" markdown>

- [**Native records**](native-records.md)

    <span class="gks-status gks-status--production">Available now</span>

    A single record or a small set. Each object is **self-contained**, with
    nothing compacted.

    *Formats: JSON, YAML*

- [**Compact records**](bundles/index.md)<span class="gks-card-badge">Bundle</span>

    <span class="gks-status gks-status--production">Available now</span>

    Package related objects together, stating **shared representations once**
    and linking to them by reference. GKM calls this **bundling**.

    *Formats: JSON, JSON Schema*

- [**Large-volume datasets**](large-datasets.md)

    <span class="gks-status gks-status--pilot">In development</span>

    Bulk formats such as **Parquet** or **relational tables** for very large
    collections, as support develops.

</div>

### Native and bundled representations

Native records carry related objects inline. Bundles place shared objects in
collections and link to them with bundle-local JSON Pointers. Below, two alleles
share a location but have different states. Native records repeat the location
and sequence reference; the bundle stores them once.

=== "Native record"

    ```json
    [
      {
        "type": "Allele",
        "location": {
          "type": "SequenceLocation",
          "sequenceReference": {
            "type": "SequenceReference",
            "refgetAccession": "SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7"
          },
          "start": 43093453,
          "end": 43093454
        },
        "state": {
          "type": "LiteralSequenceExpression",
          "sequence": "C"
        }
      },
      {
        "type": "Allele",
        "location": {
          "type": "SequenceLocation",
          "sequenceReference": {
            "type": "SequenceReference",
            "refgetAccession": "SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7"
          },
          "start": 43093453,
          "end": 43093454
        },
        "state": {
          "type": "LiteralSequenceExpression",
          "sequence": "T"
        }
      }
    ]
    ```

=== "Bundle"

    ```json
    {
      "sequenceReference": {
        "SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7": {
          "type": "SequenceReference",
          "refgetAccession": "SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7"
        }
      },
      "location": {
        "location:1": {
          "type": "SequenceLocation",
          "sequenceReference": "#/sequenceReference/SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7",
          "start": 43093453,
          "end": 43093454
        }
      },
      "allele": {
        "allele:1": {
          "type": "Allele",
          "location": "#/location/location:1",
          "state": {
            "type": "LiteralSequenceExpression",
            "sequence": "C"
          }
        },
        "allele:2": {
          "type": "Allele",
          "location": "#/location/location:1",
          "state": {
            "type": "LiteralSequenceExpression",
            "sequence": "T"
          }
        }
      }
    }
    ```

Both alleles link to the same location and keep only their distinct states. See
the cards above for format-specific guidance and examples.

## Built with community partners

The Starter Kit uses real content developed with resources such as
**[ClinVar GKM](https://dataexchange.clinicalgenome.org/clinvar-gkm/)** and
**CIViC**. Each partner defines its collection names and object
groupings in a bundle schema, preserving familiar terminology while using
shared GKM models.

This section will grow with the community's needs.
