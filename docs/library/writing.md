# Saving and exporting a bundle

Export a bundle when you want to save it, pass it to another tool, or share a
processed copy with someone else. The Starter Kit keeps the producer's format,
so existing consumers can continue to recognize its structure.

The examples use the `civic` bundle created in [Loading a bundle](loading.md).

Write the bundle to a file with `bake()`:

```python
civic.bake("out.gks.json")
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
