# Data Bundles

The GKS reference specifications let you describe a single piece of genomic
knowledge — a variant, a category of variants, a clinical assertion — as a
modular, schema-validated object. But real resources don't hold one object;
they hold thousands, and they need to hand the whole collection to someone
else. A **GKS bundle** is that hand-off: a single shareable document that
packages many modular GKS objects together under common semantics, validated
against one schema.

Because a bundle is schema-validated, the resource producing it and the tool
consuming it agree on what every field means without a side conversation. And
because it composes the same modular GKS schemas everyone else uses, a bundle
from one resource reads the same way as a bundle from another — which is what
makes knowledge from independent groups genuinely reusable rather than merely
downloadable.

## Built with community partners

The bundles in this Starter Kit are not synthetic examples. They are real
content structured together with the community resources that produce it —
groups such as **ClinVar GKS** and **CIViC**. Each partner organizes and
curates its knowledge in the way that makes sense for its own domain and
workflow; the bundle format is the shared envelope that lets that knowledge
travel. The goal is to leverage the GKS specifications, not to force every
resource into an identical shape.

!!! info "Download some datasets, register others"

    Not every resource is best delivered as a file you download. Very large
    datasets — for example **gnomAD** or the full **ClinVar GKS** corpus — can
    run to millions of records, which makes a single shippable bundle
    impractical to move, version, and keep current. For these, the intended
    model is *registration*: the resource is exposed as a live service that
    speaks GKS, and consumers query it in place rather than downloading a
    static bundle. Smaller, more stable collections ship as downloadable
    bundles. A given partner may offer both.

## The bundle, read two ways

The same bundle is a validated document for a machine and a plain sentence for
a person. Here is a trimmed example alongside how to read it.

=== "Bundle JSON"

    ```json
    {
      "bundleVersion": "1.0.0",
      "source": {
        "name": "ClinVar GKS",
        "url": "https://www.ncbi.nlm.nih.gov/clinvar/"
      },
      "statements": [
        {
          "id": "clinvar:SCV000000001",
          "direction": "supports",
          "proposition": {
            "type": "VariantPathogenicityProposition",
            "subject": { "id": "ga4gh:VA.abc123", "label": "BRCA1 c.68_69del" },
            "predicate": "isCausalFor",
            "object": {
              "id": "MONDO:0003582",
              "label": "hereditary breast-ovarian cancer syndrome"
            }
          }
        }
      ]
    }
    ```

=== "In plain language"

    This bundle was produced by **ClinVar GKS** and follows version `1.0.0` of
    the bundle format. It carries one **statement**. The statement *supports* a
    **proposition** — a possible fact — namely that the variant
    **BRCA1 c.68_69del** *is causal for* **hereditary breast-ovarian cancer
    syndrome**. The `direction` (`supports`) is the resource's stance on that
    proposition; a different resource could carry a statement that *disputes*
    the same proposition. Every identifier (`ga4gh:VA.…`, `MONDO:…`) is a
    resolvable reference, so nothing about the meaning depends on the label
    text.

The structure — `bundleVersion`, `source`, and a `statements[]` array where
each **Statement** evaluates a **Proposition** — is fixed by the schema.

## The bundle schema

Every bundle validates against a published JSON Schema. We render that schema
as a browsable, field-by-field reference so you can see exactly what a
conforming bundle must contain, which fields are required, and how a
`Statement` and its `Proposition` are shaped.

[**Read the Bundle schema →**](schemas/gks-bundle.md)

The schema shown here is a **self-contained demonstrator**: it uses local
definitions rather than remote GA4GH references so the site build stays
hermetic and reproducible. Production bundles compose the real, remote GKS
schemas — the shape is the same.

## What belongs here, and how to contribute a bundle

This section is for **packaged knowledge from a resource**: collections of
variants, conditions, propositions, and statements that another group can load
and reuse. Per-record production questions — how to mint a VRS identifier, how
to author a single VA statement — belong to each product's own documentation,
not here.

If your resource has knowledge to share and you want to package it as a GKS
bundle, see the **[Contribute](../contribute.md)** page for the bundle
contribution path, which points back to the schema above as the contract your
bundle must satisfy.
