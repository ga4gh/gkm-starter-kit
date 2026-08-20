# Bundle formats and JSON Schema

This page is for data producers preparing a bundle for others to use. It
explains what the bundle's JSON Schema must describe and how the Starter Kit
uses that information.

!!! example "CIViC example"

    The repository's CIViC bundles follow
    [`civic-gks-bundle-v0.1.0.schema.json`](bundles/civic-gks-bundle-v0.1.0.schema.json){ target="_blank" rel="noopener" }.
    Read it alongside the [example bundles](index.md#example-bundles) to see how
    the schema describes CIViC's file organization and identifies the GKM
    objects used within it.

## What all bundle formats share

The file organization can differ, but the following rules are shared:

- typed objects follow the applicable GKM schemas, and their `type` tells the
  software which GKM model to use.
- relationships to objects in the same bundle use bundle-local JSON Pointers.
- producer-specific grouping and provenance objects are permitted when their
  format schema defines them.

## Linking objects within a bundle

The current implementation expects each shared GKM object to appear once.
Relationships link to that object using an RFC 6901 JSON Pointer, which is a
path to another location in the same bundle, rather than repeating the complete
object.
The format schema defines which fields accept these links and where they lead.

The Starter Kit follows local links when requested. External identifiers in
GKM objects are preserved but not fetched. See [Exploring a loaded
bundle](../library/exploring.md) for the Python behavior.

## JSON Schema requirements

A published bundle format requires a separate JSON Schema. The current Python
API allows schema-less exploration and uses a supplied schema to check GKM
version compatibility. Full JSON Schema validation is still in development.

The `$schema` keyword belongs inside the schema file and identifies its JSON
Schema dialect. It does not link the bundle data to the schema. Consumers
currently provide both files explicitly. See [Loading a
bundle](../library/loading.md).

A format schema must:

- use JSON Schema Draft 2020-12.
- have an immutable, versioned `$id` and root `type: object`.
- define its producer-specific root collections and say which may be omitted
  or empty.
- constrain collection keys when the identifier scheme is known.
- reference the official GKM schemas with versioned GA4GH W3ID `$ref` URLs.
- match those W3ID versions to the version constants exposed by the installed
  GKM reference implementations rather than referring to a moving `latest`.
- define how local references are represented, including JSON Pointer syntax.
- state whether unknown properties are accepted, instead of leaving extension
  behavior accidental.
- describe any producer-specific fields that are outside the GKM models.

Versioned W3ID `$ref` URLs point to GKM schemas hosted online. If consumers
need to validate bundles without network access, also provide a self-contained
copy of the schema with those dependencies included.

## Producer checklist

Before publishing a bundle, confirm that:

- the JSON data and its JSON Schema are distributed together.
- identifiers are stable within the lifecycle stated by the producer.
- every local JSON Pointer resolves within the bundle.
- provenance and licensing are sufficient for downstream reuse.
- an example small enough for tests is provided.
- loading and writing the example does not lose collections, identifiers,
  references, or producer extensions.
