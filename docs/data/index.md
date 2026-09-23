# Pillar I: Data

GKM describes one piece of genomic knowledge, such as a variant, a category
of variants, or a clinical assertion, in a consistent way. Real resources
contain many of these objects and need consistent ways to share them.
**This pillar shows how GKM data can be packaged and shared in practice**,
from individual records to compact bundles and larger datasets.

## Ways to share GKM data

The right delivery method depends on the scale and the use case. The initial
implementation supports some patterns today; others are in development. The
sections below introduce each method with a short example.

<div class="grid cards" markdown>

- [**Native records**](native-records.md)

    <span class="gks-status gks-status--production">Available now</span>

    A single record or a small set. Each object is **self-contained**, with
    nothing compacted.

    *Formats: JSON, YAML*

- [**Compact records**](bundles/index.md)<span class="gks-card-badge">Bundle</span>

    <span class="gks-status gks-status--production">Available now</span>

    Package related objects together, stating **shared representations once**
    and linking to them by reference. Called **bundling** in GKM —
    [see the bundle reference pages](bundles/index.md).

    *Formats: JSON, JSON Schema*

- [**Large-volume datasets**](large-datasets.md)

    <span class="gks-status gks-status--pilot">In development</span>

    Bulk formats such as **Parquet** or **relational tables** for very large
    collections, as support develops.

</div>

### Native records

<span class="gks-status gks-status--production">Available now</span>

Share a single GKM object, or a small set, in a message or API response. The
object carries everything it needs **inline** — nothing is factored out or
referenced elsewhere. This is the atomic form the GKM reference libraries
already construct and validate.

The VRS `Allele` below is complete on its own: its `location` and
`sequenceReference` are nested directly inside it.

```json
{
  "id": "ga4gh:VA.YpMp7lIYDfsjOmHyPel8NHPgkOlL_J0B",
  "type": "Allele",
  "location": {
    "id": "ga4gh:SL.dlLI8V13wN0QF9iTu7o9DJZKn8TjXkh3",
    "type": "SequenceLocation",
    "sequenceReference": {
      "type": "SequenceReference",
      "refgetAccession": "SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7"
    },
    "start": 43093453,
    "end": 43093454
  },
  "state": {
    "type": "ReferenceLengthExpression",
    "length": 1,
    "sequence": "C",
    "repeatSubunitLength": 1
  }
}
```

This form is simple to read and produce, but when the same objects recur — in
one record or across many — repeating them in full becomes wasteful. That is
what compact records solve.

[See how native records work in practice →](native-records.md)

### Compact records

<span class="gks-status gks-status--production">Available now</span>

When shared representations appear more than once — reused within a single
record, or referenced many times across a larger set of records — a compact
record states each object **once** and links to it with a bundle-local
[JSON Pointer](https://www.rfc-editor.org/rfc/rfc6901) (a `#/...` path to another
place in the same document).

!!! note "Called *bundling* in GKM"

    Packaging records this way is known as **bundling** in GKM terminology, and
    the resulting document is a **bundle**. See the
    [bundle reference pages](bundles/index.md) for schemas, examples, and the
    public repository.

Objects of a kind are grouped into dictionary-like **collections** keyed by
identifier. In the excerpt below, one `SequenceReference` lives in the
`sequenceReference` collection, and a `SequenceLocation` refers to it by pointer
instead of nesting a copy — so the same sequence reference can be reused by any
number of locations across the bundle.

```json
{
  "sequenceReference": {
    "SQ.EJQv9rQmiD76iFmXsLwCy2dJHOFO3bpj": {
      "type": "SequenceReference",
      "refgetAccession": "SQ.EJQv9rQmiD76iFmXsLwCy2dJHOFO3bpj"
    }
  },
  "location": {
    "ga4gh:SL.DO4BZ8csWCDedM5lh7NrmIpS3RnboBHw": {
      "id": "ga4gh:SL.DO4BZ8csWCDedM5lh7NrmIpS3RnboBHw",
      "type": "SequenceLocation",
      "sequenceReference": "#/sequenceReference/SQ.EJQv9rQmiD76iFmXsLwCy2dJHOFO3bpj",
      "start": 1699,
      "end": 1700
    }
  }
}
```

A full bundle carries many such collections — variants, molecular profiles,
propositions, evidence, assertions, provenance — all wired together by pointers.
See a complete, real example in the
[CIViC mini bundles](bundles/mini-examples.md), or learn how producers define
one in [bundle schemas and contents](bundles/schemas-and-contents.md).

### Large-volume datasets

<span class="gks-status gks-status--pilot">In development</span>

A single JSON bundle works well up to a point, but some producers need to share
GKM records at a volume where one document is impractical. Work is underway on
distributing large collections of GKM records — drawn from a common set of
classes — as a **Parquet** export or a **relational database dump**, so
consumers can query them at scale without loading everything into memory.

This method is not yet available. It is being prioritized with community
partners, and this page will be updated as the format and tooling take shape.

[Read about large-volume dataset support →](large-datasets.md)

## Built with community partners

The Starter Kit uses real content developed with resources such as
**[ClinVar GKM](https://dataexchange.clinicalgenome.org/clinvar-gkm/)** and
**CIViC**. Each partner defines its collection names and object
groupings in a bundle schema, preserving familiar terminology while using
shared GKM models.

This section will grow with the community's needs.
