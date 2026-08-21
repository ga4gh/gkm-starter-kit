# Data Bundles

GKM can describe one piece of genomic knowledge, such as a variant, a category
of variants, or a clinical assertion, in a consistent way. Real resources
contain many of these objects and need to share them as a collection. A **GKM
bundle** packages a resource's related GKM objects so another group can load
and use them.

The initial Starter Kit supports bundles serialized as JSON. Other
serializations, such as JSON Lines, may be supported in the future.

Each producer defines and versions a bundle schema. The schema preserves the
resource's organization while its GKM objects retain their shared meaning.

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
