---
title: Development and contributing
---

# Development and contributing

This page explains how to set up the project for development, run tests, and update
the documentation.

!!! note "Only want to use the GKM Toolkit?"

    This page describes setting up a local source checkout for making changes. If you
    only want to install and use the published GKM Toolkit package, see [Installation](installation.md).

## Prerequisites

You will need:

- Python 3.11 or newer
- Git
- A terminal or command prompt

## Set up a virtual environment

If you are not a repository maintainer, first [fork the repository on
GitHub](https://github.com/ga4gh/gkm-starter-kit/fork). Then clone your fork
(or the main repository if you have access), enter its directory, and create a
virtual environment:

Replace `OWNER` with your GitHub username for a fork, or `ga4gh` for the main
repository.

```shell
git clone https://github.com/OWNER/gkm-starter-kit.git
cd gkm-starter-kit
python3 -m venv .venv
source .venv/bin/activate
```

## Install the development dependencies

Install all project dependencies used for code, testing, documentation, and
example notebooks:

```shell
python3 -m pip install -e '.[dev,tests,docs,notebooks]' --pre
```

!!! note "Why do I need `--pre`?"

    This project uses pre-release versions of the [GKM reference implementations](gkm.md#standards-and-reference-implementations).

## Install the pre-commit hooks

Install the hooks after installing the development dependencies:

```shell
prek install
```

## Make and check your changes

Make your changes, then run the checks that apply to them.

Run the style checks:

```shell
python3 -m ruff check .
python3 -m ruff format --check .
```

Run the test suite:

```shell
python3 -m pytest
```

## Build and preview the documentation

Generate the staged documentation and start the local documentation server:

```shell
python3 -m scripts.build_docs
zensical serve
```

Then open <http://127.0.0.1:8000>. The server reloads as you edit the source files.

Before opening a pull request, run a strict production-style build:

```shell
zensical build --clean --strict
```

## Open a pull request

Run the checks relevant to your changes, review the generated documentation, and
open a pull request on GitHub. Include a short summary of the change and any
relevant testing or documentation notes.

If the pull request resolves an issue, say so with a closing keyword such as
`Closes #123`, where `123` is the issue number. GitHub will close the issue
automatically when the pull request merges. If the pull request is related to an
issue but does not resolve it, use a non-closing reference such as `Refs #123`,
where `123` is again the issue number, or link the issue through the pull
request's GitHub interface instead.
