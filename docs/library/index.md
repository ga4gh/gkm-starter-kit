# `ga4gh.gkm` Python Package

![GKM Python package logo](../assets/images/python-package-logo.png){: width="300" style="display: block; margin: 0 auto;"}

`ga4gh.gkm` is a Python package for loading a producer's GKM
bundle, exploring its contents, following relationships, and writing it back to
JSON.

## Install

The package requires Python 3.11 or later. Install it from PyPI:

```shell
python3 -m pip install ga4gh.gkm
```

Import the bundles package:

```python
from ga4gh.gkm import bundles
```

## Supported GKM product versions

`ga4gh.gkm` supports the latest GKM product versions.
Check [compatibility](api/compatibility.md) before preparing a bundle schema.

## What you can do

- Load producer JSON with its producer-defined schema.
- Discover the collections provided by a producer.
- Work with supported values as GKM Python models.
- Follow relationships between objects without manually navigating JSON paths.
- Write the bundle back to JSON while preserving producer-specific content.
