# Mini bundle examples

Mini bundles are **small subsets of full records from a real dataset**. They let
developers trial genuine GKM data — complete, unmodified records from a community
resource — without taking on the challenge of handling a large dataset from the
start. A mini bundle is a real slice, not a simplified illustration: the records
are exactly what the producer publishes, just fewer of them.

## What's inside a mini bundle

Each mini bundle contains a handful of complete records plus everything they
depend on. The CIViC assertion 9 bundle, for example, packages one clinical
assertion together with the propositions, evidence, variants, and provenance it
references — a bounded, connected slice of CIViC:

| Collection | Records |
| --- | --- |
| assertion | 1 |
| proposition | 3 |
| evidence | 2 |
| variant | 4 |
| molecularProfile | 2 |
| disease | 1 |
| source | 3 |
| method | 1 |

Because the whole slice fits in one small file, you can load it, inspect it, and
build against real GKM structures immediately, then scale up to a
[full published bundle](repository.md) once your code works.

## A complete record from the bundle

The record below is the actual [CIViC Assertion 9](https://civicdb.org/links/assertion/9),
carried in the bundle exactly as CIViC publishes it — a real Tier II
clinical-significance statement with its guideline classification and evidence
lines. It links to its proposition, method, sources, and evidence elsewhere in
the same bundle rather than repeating them:

```json
{
  "id": "civic.aid:9",
  "type": "Statement",
  "description": "ACVR1 G328V mutations occur within the kinase domain, leading to activation of downstream signaling. Exclusively seen in high-grade pediatric gliomas, supporting diagnosis of diffuse intrinsic pontine glioma.",
  "specifiedBy": "#/method/civic.method:2019",
  "reportedIn": [
    "https://civicdb.org/links/assertion/9",
    "#/source/civic.sid:2149",
    "#/source/civic.sid:2680"
  ],
  "proposition": "#/proposition/civic.proposition:f0SrtLbW05PqfqLs-hOK4tZxI3xO3kMO",
  "direction": "supports",
  "strength": {
    "primaryCoding": {
      "system": "AMP/ASCO/CAP Guidelines, 2017",
      "code": "potential"
    }
  },
  "classification": {
    "name": "Tier II",
    "primaryCoding": {
      "system": "AMP/ASCO/CAP Guidelines, 2017",
      "code": "tier ii"
    }
  },
  "hasEvidenceLines": [
    {
      "type": "EvidenceLine",
      "targetProposition": "#/proposition/civic.proposition:gGPvwGKtZSs7Me0eqveHyfB2zKj1QXX6",
      "hasEvidenceItems": [
        "#/evidence/civic.eid:4846",
        "#/evidence/civic.eid:6955"
      ],
      "directionOfEvidenceProvided": "supports",
      "strengthOfEvidenceProvided": {
        "primaryCoding": {
          "system": "AMP/ASCO/CAP Guidelines, 2017",
          "code": "C"
        }
      }
    }
  ]
}
```

Open the full files below to see this assertion alongside the propositions,
evidence, variants, and molecular profiles it connects to.

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
