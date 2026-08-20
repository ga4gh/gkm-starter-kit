# CIViC notebook examples

This directory contains two small examples of the CIViC GKM Bundle format.
Both use referenced JSON: shared GKM objects live in root collections, and
relationships use bundle-local JSON Pointers.

## Included bundles

`civic-aid-9-bundle.json` represents CIViC Assertion 9. It carries a Tier II
clinical-significance assertion under the AMP/ASCO/CAP Guidelines (2017), plus
the diagnostic propositions and evidence used by the assertion.

`civic-aid-251-bundle.json` represents CIViC Assertion 251. It carries a
likely-oncogenic assertion under the ClinGen/CGC/VICC Guidelines for
Oncogenicity (2022).

`civic-gks-bundle-v0.1.0.schema.json` is the JSON Schema for both examples. It
defines the CIViC-specific collections and composes the relevant GKM schemas.

The full CIViC export is intentionally excluded. These small bundles are easier to
inspect and commit while still exercising different VA-Spec assertion types.

Open `explore-civic-bundles.ipynb` for a guided walkthrough.
