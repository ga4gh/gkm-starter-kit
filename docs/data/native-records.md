# Native records

A **native record** is a single GKM object — a variant, a category of variants,
or a clinical assertion — written out on its own, with everything it needs
**inline**. Nothing is factored out into shared collections and nothing is
linked by reference. This is how GKM records work in practice before any
[bundling](bundles/index.md) features are applied.

Native records are the right choice when you are exchanging one record, or a
small set, in a message or an API response, and readability matters more than
avoiding repetition.

## A single record

The example below is a complete VRS `Allele`. Its `location` and
`sequenceReference` are nested directly inside it, so the record stands entirely
on its own. The same object can be serialized as **JSON** or **YAML** — the
structure is identical.

=== "JSON"

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

=== "YAML"

    ```yaml
    id: ga4gh:VA.YpMp7lIYDfsjOmHyPel8NHPgkOlL_J0B
    type: Allele
    location:
      id: ga4gh:SL.dlLI8V13wN0QF9iTu7o9DJZKn8TjXkh3
      type: SequenceLocation
      sequenceReference:
        type: SequenceReference
        refgetAccession: SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7
      start: 43093453
      end: 43093454
    state:
      type: ReferenceLengthExpression
      length: 1
      sequence: C
      repeatSubunitLength: 1
    ```

Every typed object carries a `type`, which tells GKM software which model to use
when it reads the record. Because the record is self-contained, a consumer can
validate and interpret it without any other context.

## A small set of records

A small set of native records is simply a list of complete objects. Each entry
repeats everything it needs, even if two records happen to share a value.

```json
[
  {
    "id": "ga4gh:VA.YpMp7lIYDfsjOmHyPel8NHPgkOlL_J0B",
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
    "state": {"type": "LiteralSequenceExpression", "sequence": "C"}
  },
  {
    "id": "ga4gh:VA.example2",
    "type": "Allele",
    "location": {
      "type": "SequenceLocation",
      "sequenceReference": {
        "type": "SequenceReference",
        "refgetAccession": "SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7"
      },
      "start": 43093500,
      "end": 43093501
    },
    "state": {"type": "LiteralSequenceExpression", "sequence": "T"}
  }
]
```

## When to move beyond native records

Native records stay simple as long as the set is small and repetition is
limited. When the same objects recur many times — reused within one record, or
referenced across a larger set — restating them in full becomes wasteful and
harder to keep consistent.

At that point, a **compact record** states each shared object once and links to
it by reference. In GKM terminology this is called **bundling**.

[Learn about bundles →](bundles/index.md)
