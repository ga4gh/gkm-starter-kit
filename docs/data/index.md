# Data

GKM describes one piece of genomic knowledge — a variant, a category of
variants, or a clinical assertion — in a consistent way. Real resources hold
many of these objects and need to share them as **collections**.

How you share those collections depends on scale and use case. There are
different ways to share depending on what you need: a single record in a
message, a compact bundle of many related records, or a large-volume dataset in
a bulk format. This page walks through those methods and what the Starter Kit
supports today.

## Ways to share GKM data

Choose a method by scale and use case — from a single record to bulk datasets.

### One record at a time <span class="gks-status gks-status--production">Available</span>

A single GKM object — a variant, a category of variants, or a clinical
assertion — exchanged in a message or API response. This is the atomic case the
GKM reference libraries already construct and validate.

### Compact bundles of many records <span class="gks-status gks-status--production">Available</span>

Package many related objects into one document and state shared representations
once, referencing them by a bundle-local pointer instead of repeating them.
This is today's JSON bundle workflow (see below). Line-delimited JSON (JSON
Lines) is <span class="gks-status gks-status--proposal">Considering</span>.

### Large-volume datasets in multiple formats <span class="gks-status gks-status--pilot">In development</span>

For datasets too large to share as a single JSON document, GKM knowledge can be
distributed in bulk-friendly formats such as **JSON Lines**, **Parquet**, and
**relational tables**. Support for these is being developed and prioritized with
community partners.

## Bundle terminology

- A **bundle** is a collection of related GKM objects from a producer.
- A **bundle schema** is the separate JSON Schema that defines how a producer
  organizes its bundles, including their collections, metadata, and local
  references.

The current workflow stores each bundle in a JSON file and distributes it with
its bundle schema. Multiple bundles can share the same bundle schema.

## Bundle contents

A producer groups related objects into named **collections**, such as sources
or evidence. This simplified JSON shows how two collections can link related
objects; it is not a complete bundle:

```json
{
  "sources": {
    "source-1": {
      "type": "Document",
      "title": "Example study"
    }
  },
  "evidence": {
    "evidence-1": {
      "type": "Statement",
      "reportedIn": ["#/sources/source-1"]
    }
  }
}
```

`sources` and `evidence` are collection names. Within each collection,
identifiers such as `source-1` map to GKM objects.

Strings that begin with `#/` are bundle-local JSON Pointers. The evidence links
to its source without repeating the source object.

## Built with community partners

The Starter Kit uses real content developed with resources such as **ClinVar
GKS** and **CIViC**. Each partner defines its collection names and object
groupings in a bundle schema, preserving terminology familiar to its users
while using shared GKM models.

!!! info "Bundles are one distribution option"

    GKM does not require every resource to distribute bundles.
    The Data Bundles pillar supports resources that choose to package related
    GKM objects as bundles. Other distribution methods are outside the scope of
    this pillar.
