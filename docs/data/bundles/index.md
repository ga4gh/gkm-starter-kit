# Bundles

GKM bundles package **related genomic knowledge** so it can be **shared,
validated, and reused across resources** without losing meaning. They keep
standard GKM objects connected while preserving the **producer’s organization
and context**, giving producers **flexibility in how they structure their
data**.

## What a bundle looks like

A bundle groups related GKM objects into named **collections**. A producer
defines the collections and their contents in a bundle schema. Relationships
between objects in the same bundle use bundle-local JSON Pointers (`#/...`).

This example has required metadata, a shared data-release extension, and two
samples. Both samples point to the same extension, so its value appears once.

```json
{
  "metadata": {
    "createdAt": "2026-09-21",
    "producer": "Example knowledgebase",
    "bundleVersion": "1.0"
  },
  "extensions": {
    "data-release": {
      "type": "Extension",
      "name": "dataRelease",
      "value": "2026-09"
    }
  },
  "samples": {
    "sample:1": {
      "id": "sample:1",
      "type": "Sample",
      "name": "Tumor sample",
      "dataRelease": "#/extensions/data-release"
    },
    "sample:2": {
      "id": "sample:2",
      "type": "Sample",
      "name": "Normal sample",
      "dataRelease": "#/extensions/data-release"
    }
  }
}
```

Each shared GKM object appears once in a bundle. Other objects link to it with a
JSON Pointer instead of repeating it. Bundles are distributed with their bundle
schema, which defines the collection names, allowed objects, metadata, and local
references.

## Continue exploring

<div class="grid cards" markdown>

- :material-file-tree: [**Define bundle schemas**](schemas-and-contents.md)

    Define collections, metadata, and the GKM objects they contain.

- :material-eye-outline: [**Inspect bundle examples**](examples.md)

    Explore small, focused subsets of producers' actual published data.

- :material-database-arrow-down: [**Browse complete public bundles**](repository.md)

    Download producers' complete published datasets and schemas.

</div>
