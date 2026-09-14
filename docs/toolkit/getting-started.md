# Getting started

The GKM Toolkit lets you bring published genomic knowledge into Python, follow
the links between related records, and save just the knowledge your application
needs. This getting-started guide demonstrates the core ingest-and-integrate
pattern—load a validated bundle, resolve local relationships, and export a
focused result—using CIViC as an example.

!!! note

    This guide assumes you have completed the [installation](installation.md)
    steps and have the GKM Toolkit available in your Python environment.

## Explore published datasets

See which published datasets are available in the Starter Kit repository:

```python
from ga4gh.gkm.bundles import BundleRepository, load_repository_bundle

repository = BundleRepository(refresh=False)
print("Available resources:", repository.resource_names)
```

Expected output:

```text
Available resources: ('civic',)
```

The repository currently includes CIViC. The rest of this walkthrough uses it,
but the same pattern works with any name the repository lists.

## Load the CIViC knowledge

Bring the published CIViC bundle into your application:

```python
civic = load_repository_bundle(repository, "civic", refresh=False)
print(f"Loaded {civic.name}")
```

Expected output:

```text
Loaded civic
```

By default, the Toolkit uses saved local artifacts when available, then
validates the bundle and schema before you work with the data.

## Follow the connected knowledge

Now that the knowledge is available locally, choose one clinical assertion and
follow the records it connects. This one links a classification to a proposition
about a variant and a condition:

```python
assertion = civic.assertion["civic.aid:9"]
proposition = civic.resolve(assertion["proposition"])
variant = civic.resolve(proposition.subjectVariant)
condition = civic.resolve(proposition.objectCondition)

print("Classification:", assertion["classification"]["name"])
print("Variant:", variant.name)
print("Condition:", condition.root.name)
```

Expected output:

```text
Classification: Tier II
Variant: ACVR1 G328V
Condition: Diffuse Midline Glioma, H3 K27-altered
```

This is the integration step: the Toolkit follows the links in the bundle so
your application can use related knowledge together.

## Export a result for your application

Finally, save just this connected slice of knowledge as a standalone JSON file
for your application to use or pass on:

```python
import json
from pathlib import Path

payload = {"source": "CIViC", "assertion": civic.export(assertion, deep=True)}
output_path = Path("civic-integrated-knowledge.json")
output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {output_path}")
```

Expected output:

```text
Wrote civic-integrated-knowledge.json
```

The JSON file contains that assertion, its proposition, and the referenced
knowledge expanded inline.

For another published dataset, choose a name from `repository.resource_names`
and replace `"civic"`.

## Continue with the Toolkit

<div class="grid cards" markdown>

- :material-notebook-outline: [**See examples**](notebooks/index.md)

    Read guided notebook examples online, or learn how to run them yourself.

- :material-database: [**Explore available data**](../data/bundles/repository.md)

    Learn about the public bundle repository and its published datasets.

- :material-language-python: [**Python API Reference**](api/index.md)

    Read the API documentation for the package and its functionality.

- :material-file-search-outline: [**Preview example data**](../data/bundles/mini-examples.md)

    Inspect a compact, mini bundles and the linked records it contains.

</div>
