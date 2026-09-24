# Bundle schemas and contents

This page is for data producers preparing a bundle for others to use. It
defines collection names, object groupings, metadata, and GKM object types with
JSON Schema. For an overview of bundle contents and JSON Pointers, see
[Bundles](index.md).

## Define a bundle schema

Use these rules when authoring a bundle schema.

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

## Producer checklist

Before distributing a bundle, confirm that:

- the bundle and its bundle schema are distributed together.
- identifiers are stable within the lifecycle stated by the producer.
- every bundle-local JSON Pointer resolves within the bundle.
- provenance and licensing are sufficient for downstream reuse.
