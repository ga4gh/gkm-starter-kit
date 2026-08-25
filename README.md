# GKM Starter Kit

A practical entry point for using the GA4GH Genomic Knowledge Model (GKM).

**Live site:** <https://ga4gh.github.io/gks-starter-kit/>

The Starter Kit brings together three complementary resources:

- **Data Bundles** package related GKM objects from participating producers.
- **`ga4gh.gkm`** provides Python tools for loading and working with those bundles.
- **Vignettes** show how implementers use GKM standards to solve real problems.

Start with the [documentation](https://ga4gh.github.io/gks-starter-kit/) for an
overview, examples, and API details.

## Contributing a vignette

1. Read the [contribution guide](https://ga4gh.github.io/gks-starter-kit/contribute/) on the live site.
2. Either:
    - Open a [**Propose a vignette**](https://github.com/ga4gh/gks-starter-kit/issues/new?template=propose-vignette.yml) issue, or
    - Copy `docs/vignettes/_template/vignette.md` into a new `docs/vignettes/<slug>/` folder, fill it in, and open a PR.

## `ga4gh.gkm` Python package

[![image](https://img.shields.io/pypi/v/ga4gh.gkm.svg)](https://pypi.org/project/ga4gh.gkm/)
[![image](https://img.shields.io/pypi/l/ga4gh.gkm.svg)](https://pypi.org/project/ga4gh.gkm/)
[![image](https://img.shields.io/pypi/pyversions/ga4gh.gkm.svg)](https://pypi.org/project/ga4gh.gkm/)
[![Actions status](https://github.com/ga4gh/gks-starter-kit/actions/workflows/checks.yaml/badge.svg)](https://github.com/ga4gh/gks-starter-kit/actions/workflows/checks.yaml)

### Installation

Install from [PyPI](https://pypi.org/project/ga4gh.gkm/):

```shell
python3 -m pip install ga4gh.gkm
```

## Development

Clone the repo and create a virtual environment:

```shell
git clone https://github.com/ga4gh/gks-starter-kit
cd gks-starter-kit
python3 -m venv venv
source venv/bin/activate
```

Install development dependencies and `prek`:

```shell
python3 -m pip install -e '.[dev,tests,docs,notebooks]'
prek install
```

Check style with `ruff`:

```shell
python3 -m ruff check .
python3 -m ruff format --check .
```

Run tests with `pytest`:

```shell
pytest
```

## Docs

```shell
mkdocs serve
```

Then open <http://127.0.0.1:8000>.

## License

[CC0 1.0 Universal](LICENSE)
