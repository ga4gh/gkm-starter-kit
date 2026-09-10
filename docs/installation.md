---
title: Installation
---

# Installation

This page explains how to install the Genomic Knowledge Model (GKM) Toolkit and choose
the optional dependencies you need.

!!! note "Want to contribute to the GKM Toolkit?"

    This page describes installing the published GKM Toolkit package for using it. If you
    want to make code or documentation changes, use the editable source checkout and
    development dependencies described in [Development and contributing](development.md).

!!! note "Only want to read the notebooks?"

    No installation is needed. Go to [Explore with notebooks](library/notebooks/index.md)
    to read the rendered walkthroughs online.

## Prerequisites

You will need:

- Python 3.11 or newer
- Git
- A terminal or command prompt

## Set up a virtual environment

To use the example notebooks and data included in this repository, clone the repository,
create a virtual environment, and activate it:

```shell
git clone https://github.com/ga4gh/gkm-starter-kit.git
cd gkm-starter-kit
python3 -m venv .venv
source .venv/bin/activate
```

## Install the GKM Toolkit

With the virtual environment activated, install the published GKM Toolkit package
from PyPI:

```shell
python3 -m pip install ga4gh.gkm --pre
```

!!! note "Why do I need `--pre`?"

    This project uses pre-release versions of the [GKM reference implementations](gkm.md#standards-and-reference-implementations).

### Optional dependencies

Most users can start with the GKM Toolkit package alone. Add these extras only
when you need the related capability:

- **`notebooks`** — Run the example notebooks.
- **`tests`** — Run the test suite.
- **`dev`** — Change the GKM Toolkit's code and run code-quality checks.
- **`docs`** — Build or edit the documentation.

You can install more than one at a time by separating them with commas. For
example, this installs all optional dependencies:

```shell
python3 -m pip install "ga4gh.gkm[notebooks,tests,dev,docs]" --pre
```

## Now that you're set up

Choose what you want to do next:

<div class="grid cards" markdown>

- :material-notebook-outline: [**See the examples**](library/notebooks/index.md)

    Read the rendered notebooks online, or learn how to run them locally.

- :material-database: [**Work with GKM data**](data/index.md)

    Browse bundles, schemas, and public data resources.

- :material-language-python: [**Python API Reference**](library/api/index.md)

    Read the API documentation for the package and its functionality.

- :material-source-pull: [**Contribute to the GKM Toolkit**](development.md)

    Contribute code, documentation, or a user story to the GKM Toolkit.

</div>
