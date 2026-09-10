# Bundle schemas and contents

This page is for data producers preparing a bundle for others to use. It
explains how to define collection names, object groupings, metadata, and GKM
object types with JSON Schema.

## General concepts

### Bundle terminology

- A **bundle** is a collection of related GKM objects from a producer.
- A **bundle schema** defines the bundle’s collections, metadata, and local
  references.

### What all bundles share

Collection names and object groupings can differ, but the following rules are
shared:

- typed objects follow the applicable GKM product schemas, and their `type`
  tells the software which GKM model to use.
- relationships to objects in the same bundle use bundle-local JSON Pointers.
- producer-specific collections, metadata, and provenance objects are
  permitted when the bundle schema defines them.

## Define a bundle schema

### Schema requirements

Each producer defines a separate bundle schema for its bundles. To share
bundles through the Data Bundles pillar, the bundle schema must:

- use JSON Schema Draft 2020-12, declared with
  `"$schema": "https://json-schema.org/draft/2020-12/schema"`.
- define an object at the schema root with `"type": "object"`.
- define its root collections and any producer-specific metadata or provenance
  fields.
- reference the official GKM product schemas with versioned GA4GH W3ID `$ref`
  URLs that are compatible with the GKM reference implementations used to load
  the bundle.
    - For example,
      `"$ref": "https://w3id.org/ga4gh/schema/gks-core/1.1.0/json/MappableConcept"`
      selects `MappableConcept` from GKS-Core version 1.1.0.

### Recommendations

To make a bundle schema's intent explicit:

- list collections that must appear with `required`.
- use `minProperties` when a collection must not be empty.
- set `additionalProperties` to state whether unknown fields are accepted.
- use `patternProperties` when collection identifiers follow a known pattern.

## Create bundle contents

### Collections and relationships

A producer groups related objects into named **collections**, such as sources or
evidence. This simplified example shows how collections can link related
objects:

```json
{
  "sources": {
    "source-1": {"type": "Document", "title": "Example study"}
  },
  "evidence": {
    "evidence-1": {
      "type": "Statement",
      "reportedIn": ["#/sources/source-1"]
    }
  }
}
```

The evidence links to its source with a bundle-local JSON Pointer instead of
repeating the source object.

### Shared representations

A producer packages related GKM objects into one document and states each
shared representation once. Consumers can then resolve relationships without
re-reading repeated objects.

Each shared GKM object appears once in a bundle. Relationships link to that
object using an RFC 6901 JSON Pointer, which is a path to another location in
the same bundle, rather than repeating the complete object.

The current workflow uses JSON bundles distributed with their bundle schema.
Other serializations may be supported in the future.

## Producer checklist

Before distributing a bundle, confirm that:

- the bundle and its bundle schema are distributed together.
- identifiers are stable within the lifecycle stated by the producer.
- every bundle-local JSON Pointer resolves within the bundle.
- provenance and licensing are sufficient for downstream reuse.
