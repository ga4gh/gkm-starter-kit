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

A producer groups related objects into named **collections**. The bundle schema
defines the collection names and the objects allowed in each. Bundle contents
store objects in those collections.

Use bundle-local JSON Pointers to link objects in the same bundle. Each pointer
identifies a shared object elsewhere in the bundle. This lets the bundle store
the object once and reuse it.

### Shared representations

A producer packages related GKM objects into one document and states each
shared representation once. Consumers can then resolve relationships without
re-reading repeated objects.

Each shared GKM object appears once in a bundle. Relationships link to that
object using an RFC 6901 JSON Pointer, which is a path to another location in
the same bundle, rather than repeating the complete object.

The current workflow uses JSON bundles distributed with their bundle schema.
Other serializations may be supported in the future.

### Example

This example shows how a bundle schema defines the contents a bundle must have.
The bundle includes required metadata, a shared standard `Extension`, and two
producer-specific `Sample` objects. The versioned W3ID `$ref` points to the
GKS-Core schema for `Extension`.

#### Bundle schema

The schema requires metadata, extensions, and samples, and defines what they
contain.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["createdAt", "producer", "bundleVersion"],
      "properties": {
        "createdAt": {"type": "string"},
        "producer": {"type": "string"},
        "bundleVersion": {"type": "string"}
      }
    },
    "extensions": {
      "type": "object",
      "minProperties": 1,
      "additionalProperties": {
        "$ref": "https://w3id.org/ga4gh/schema/gks-core/1.1.0/json/Extension"
      }
    },
    "samples": {
      "type": "object",
      "minProperties": 1,
      "additionalProperties": false,
      "patternProperties": {
        "^sample:[0-9]+$": {
          "type": "object",
          "required": ["id", "type", "name", "dataRelease"],
          "properties": {
            "id": {"type": "string"},
            "type": {"const": "Sample"},
            "name": {"type": "string"},
            "dataRelease": {
              "type": "string",
              "pattern": "^#/extensions/"
            }
          }
        }
      }
    }
  },
  "required": ["metadata", "extensions", "samples"]
}
```

#### Bundle contents

The bundle includes the required metadata, one data-release extension, and two
samples that use it.

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

#### How they work together

This table shows how the bundle schema relates to the bundle contents in this
example.

In this example, `extensions` and `samples` are collections. Their keys, such
as `data-release` and `sample:1`, identify the objects they contain.

| Schema feature | What it means in this bundle |
| --- | --- |
| `required` | A valid bundle includes `metadata`, `extensions`, `samples`, and the required metadata fields. |
| `minProperties` | The `extensions` and `samples` collections cannot be empty. |
| `additionalProperties` | Extension keys have no required pattern. Producers may use names such as `data-release` and `license`; each value is an `Extension`. |
| `patternProperties` | Sample keys follow the `sample:<number>` pattern, such as `sample:1`. |
| `$ref` | Each `extensions` value uses the GKS-Core `Extension` schema, identified by its GA4GH W3ID URL. |
| Bundle-local JSON Pointer | Both samples point to `#/extensions/data-release`, so the release value is stored once. |

## Producer checklist

Before distributing a bundle, confirm that:

- the bundle and its bundle schema are distributed together.
- identifiers are stable within the lifecycle stated by the producer.
- every bundle-local JSON Pointer resolves within the bundle.
- provenance and licensing are sufficient for downstream reuse.
