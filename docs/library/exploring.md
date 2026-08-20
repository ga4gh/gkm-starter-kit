# Exploring a loaded bundle

After loading a bundle, you can discover its collections, work with GKM
objects, and follow links between them. The snippets below use the `civic`
bundle created in [Loading a bundle](loading.md).

## Explore collections

`collection_names()` shows how the producer organized the bundle:

```python
civic.collection_names()
```

The Starter Kit preserves the producer's collection names. Access a collection
with an attribute, standard mapping syntax, or `collection()`:

```python
civic.sequenceReference
civic["sequenceReference"]
civic.collection("sequenceReference")
```

Collections map the producer's identifiers to their objects:

```python
sequence_reference = civic.sequenceReference[
    "SQ.6CnHhDq_bDCsuIBf0AzxtKq_lXYM7f0m"
]
```

## Work with GKM objects

When possible, the Starter Kit loads an object with its GKM Python model. This
provides validation, a known type, and attribute access:

```python
from ga4gh.vrs.models import SequenceReference

assert isinstance(sequence_reference, SequenceReference)
```

## Follow relationships

Objects in a bundle can link to one another with local JSON Pointers. Use
`resolve()` to follow one link:

```python
proposition = civic.resolve(
    civic.assertion["civic.aid:9"]["proposition"]
)
```

Use `dereference()` when you need a JSON-compatible view with all reachable
local links expanded:

```python
complete_proposition = civic.dereference(proposition)
```

The original bundle remains unchanged. External identifiers are not fetched.

See the [Models API](api/models.md) for collection access, reference handling,
and errors. The [CIViC walkthrough](civic-notebook.md) shows these operations
with saved output.
