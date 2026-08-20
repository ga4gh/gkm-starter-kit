# Data Bundles

GKM can describe one piece of genomic knowledge, such as a variant, a category
of variants, or a clinical assertion, in a consistent way. Real resources
contain many of these objects and need to share them as a collection. A **GKM
bundle** is a JSON document that packages a resource's GKM objects so another
group can load and use them.

Each producer defines and versions its bundle format. This preserves the
resource's organization while its GKM objects retain their shared meaning.

## What a bundle contains

A bundle has two parts that are distributed together but remain separate:

- a **JSON data document**, containing the knowledge being shared and the
  producer's organization and source information; and
- a **JSON Schema**, describing that organization and identifying the GKM
  standards used by the data.

The data and schema are separate files distributed together. See [Bundle
formats and JSON Schema](formats.md) for publishing requirements.

A producer groups related objects into named **collections**, such as variants
or assertions. An object can link to another object in the same bundle instead
of repeating it. Producers keep the collection names and organization their
users already know. GKM standardizes the objects inside, not every name in the
file.

## Built with community partners

The Starter Kit uses real content developed with resources such as **ClinVar
GKS** and **CIViC**. Each partner keeps the organization appropriate for its
domain while using shared GKM models.

!!! info "Download some datasets, query others"

    Not every resource is best delivered as a file you download. Very large
    datasets, such as **gnomAD** or the full **ClinVar GKS** corpus, may contain
    millions of records. These can be registered as live GKM services that
    consumers query in place. Smaller collections can be downloadable bundles;
    a partner may offer both.

    This service registration is a distribution concept. It is distinct from
    the Python package's local catalog, which gives bundle files short names
    for loading.

## Example bundles

These two small bundles exercise different VA-Spec assertion types. Both
follow the
[`civic-gks-bundle-v0.1.0.schema.json`](bundles/civic-gks-bundle-v0.1.0.schema.json){ target="_blank" rel="noopener" }
schema.

- [**`civic-aid-9-bundle.json`**](bundles/civic-aid-9-bundle.json){ target="_blank" rel="noopener" }
  represents CIViC Assertion 9: a Tier II clinical-significance assertion
  under the AMP/ASCO/CAP Guidelines (2017), together with its diagnostic
  propositions and evidence.
- [**`civic-aid-251-bundle.json`**](bundles/civic-aid-251-bundle.json){ target="_blank" rel="noopener" }
  represents CIViC Assertion 251: a likely-oncogenic assertion under the
  ClinGen/CGC/VICC Guidelines for Oncogenicity (2022).

The full CIViC export is not included. These smaller examples are easy to
inspect but still show distinct assertion models. The [CIViC
notebook](../library/civic-notebook.md) loads and compares them.

## Next steps

- To package and publish your resource's GKM objects, read the [bundle format
  and JSON Schema requirements](formats.md).
- To load and work with an existing bundle, continue to the [Python
  package](../library/index.md).
