# Loading a bundle

`load_bun()` loads a JSON bundle and makes its collections available in
Python. Provide the producer's JSON Schema so the Starter Kit can check that
its GKM versions match the installed reference libraries.

!!! info "CIViC example files"

    Run this code from the repository root, or replace these paths with your
    own bundle and schema.

    {{ bundle_linkouts("../data/bundles", "civic-aid-9-bundle.json", "civic-gks-bundle-v0.1.0.schema.json") }}

```python
from gkm import starter

civic = starter.load_bun(
    "notebooks/civic/bundles/civic-aid-9-bundle.json",
    schema="notebooks/civic/bundles/civic-gks-bundle-v0.1.0.schema.json",
)
```

Bundles and schemas can come from local files, readable JSON streams, or names
registered in the bundle catalog. A registration can keep the data, schema,
and producer information together under one short name.

## GKM version compatibility

When a schema is provided, `load_bun()` checks its versioned GA4GH W3ID
references against the installed GKM libraries. This prevents the data from
being interpreted with incompatible models. It is not full JSON Schema
validation.

Use `supported_gkm_versions()` to see the versions supported by the current
environment:

```python
starter.supported_gkm_versions()
```

See the [Loading API](api/loading.md), [Compatibility
API](api/compatibility.md), and [Catalog API](api/catalog.md) for accepted
inputs, registration, and errors.
