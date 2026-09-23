# Mini bundle examples

Mini bundles are small, focused subsets of a producer's complete dataset. They
pair representative GKM data from a community resource with its bundle schema,
making the bundle's structure and relationships easier to inspect. They are not
complete published datasets.

## What a mini bundle shows

Each bundle groups objects into dictionary-like **collections** keyed by
identifier, and links related objects with bundle-local JSON Pointers so a
shared object is stated once and reused. The excerpt below, taken from the
CIViC assertion 9 bundle, shows a `SequenceLocation` referring to a
`SequenceReference` by pointer rather than nesting a copy:

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
      "type": "SequenceLocation",
      "sequenceReference": "#/sequenceReference/SQ.EJQv9rQmiD76iFmXsLwCy2dJHOFO3bpj",
      "start": 1699,
      "end": 1700
    }
  }
}
```

Open the full files below to see how variants, molecular profiles,
propositions, evidence, and assertions are wired together the same way.

## CIViC

These two CIViC mini bundles show different VA-Spec assertion types. Both use
the [`civic-gks-bundle-v0.1.0.schema.json`](civic-gks-bundle-v0.1.0.schema.json){ target="_blank" rel="noopener" }
bundle schema.

- [**`civic-assertion-9-bundle.json`**](civic-assertion-9-bundle.json){ target="_blank" rel="noopener" }
  represents [CIViC Assertion 9](https://civicdb.org/links/assertion/9): a Tier II
  clinical-significance assertion under the AMP/ASCO/CAP Guidelines (2017), together
  with its diagnostic propositions and evidence.
- [**`civic-assertion-251-bundle.json`**](civic-assertion-251-bundle.json){ target="_blank" rel="noopener" }
  represents [CIViC Assertion 251](https://civicdb.org/links/assertion/251): a
  likely-oncogenic assertion under the ClinGen/CGC/VICC Guidelines for Oncogenicity
  (2022).
