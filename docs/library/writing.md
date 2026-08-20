# Saving and exporting a bundle

Export a bundle when you want to save it, pass it to another tool, or share a
processed copy with someone else. The Starter Kit keeps the producer's format,
so existing consumers can continue to recognize its structure.

!!! note "Scope of bundle export"

    This page describes the Starter Kit's file-based workflow. The ability to
    export a bundle does not make bundles required or establish them as the
    preferred way to share all GKM data. Applications can also exchange
    individual objects through the GKM reference implementations or query GKM
    resources through service APIs. See [Ways to use
    GKM](../why.md#ways-to-use-gkm) for those options.

The examples use the `civic` bundle created in [Loading a bundle](loading.md).

Write the bundle to a file with `write()`:

```python
civic.write("out.gks.json")
```

Use `to_dict()` when another part of your application needs JSON-compatible
Python values:

```python
document = civic.to_dict()
```

## What writing preserves

Writing preserves producer collection names, identifiers, local links,
metadata, and producer-specific values. The result may not be byte-for-byte
identical to the input, but it retains the bundle's meaning and organization.

The current writer does not validate the output against the producer's schema.
See the [Models API](api/models.md) for serialization options and detailed
behavior.
