# GKS Starter Kit

A single community-facing entry point for the GA4GH Genomic Knowledge Standards (GKS) ecosystem.

**Live site:** https://ga4gh.github.io/gks-starter-kit/

The Starter Kit collects real-world **vignettes** — concise walk-throughs of high-value uses of GKS, each with the actual data and tools needed to deliver the use case. They're designed to be share-friendly so adopters can carry the value proposition to their teams, leadership, and broader communities.

## Contributing a vignette

1. Read the [contribution guide](https://ga4gh.github.io/gks-starter-kit/contribute/) on the live site.
2. Either:
    - Open a [**Propose a vignette**](https://github.com/ga4gh/gks-starter-kit/issues/new?template=propose-vignette.yml) issue, or
    - Copy `docs/vignettes/_template/vignette.md` into a new `docs/vignettes/<slug>/` folder, fill it in, and open a PR.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Then open http://127.0.0.1:8000.

## Repository layout

- `docs/` — mkdocs source
- `docs/index.md`, `docs/about.md`, `docs/contribute.md` — top-level reader pages
- `docs/vignettes/` — vignette folders, one per use case
- `docs/vignettes/_template/` — canonical template + authoring guide
- `docs/vignettes/patterns.yml` — controlled vocabulary for the `pattern` frontmatter field
- `main.py` — mkdocs-macros entrypoint (catalog rendering)
- `scripts/vignette_loader.py` — shared frontmatter parser (single source of truth, imported by both `main.py` and `gen_filter_pages.py`)
- `scripts/gen_filter_pages.py` — generates per-axis filter pages at build time
- `.github/workflows/publish.yml` — GitHub Action that deploys to GitHub Pages on push to `main`
- `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md` — contribution forms

## Initial GitHub Pages setup

After the first push of `main` to GitHub:

1. Wait for the publish workflow's first run to complete (Actions tab). `mkdocs gh-deploy` creates the `gh-pages` branch on first run.
2. In Settings → Pages, set Source = "Deploy from a branch", Branch = `gh-pages`, Folder = `/ (root)`.
3. Confirm the workflow succeeds on subsequent pushes and the site is reachable at the GitHub Pages URL.
4. Update `site_url` in `mkdocs.yml` and the "Live site" link above if the canonical URL differs.

## License

[Apache 2.0](LICENSE)
