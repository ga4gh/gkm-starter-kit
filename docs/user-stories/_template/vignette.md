---
title: "<One-line use case>"
slug: <kebab-case-slug-matching-vignette-folder-name>
summary: "<One-sentence catalog blurb. Distinct from 'Why this matters' below.>"
products:
  - name: VRS              # one of: GKS-Core, VRS, Cat-VRS, VA-Spec
    version: "2.0"
pattern: <one value from docs/user-stories/patterns.yml>
implementer: <organization, consortium, knowledgebase, or project>
notebook:                    # optional executable walkthrough
  path: <source>/<slug>/notebook.md
status: production         # one of: production | pilot | proposal
contributors:
  - <GitHub handle or name>
last_updated: 2026-05-27
---

# <Your one-line use case: the title as it should appear in the rendered page (match the `title` frontmatter field above)>

**Why this matters**

<3–5 sentence plain-language paragraph. This is the forwardable bit, written so a non-technical reader could quote it. No jargon, no acronyms without expansion.>

**At a glance**

- **Implementer:** <implementer>
- **Products:** <span class="gks-product-label gks-product-label--vrs">VRS <small>2.0</small></span> <span class="gks-product-label gks-product-label--va-spec">VA-Spec <small>1.0</small></span>
- **Pattern:** <pattern label from `patterns.yml`>
- **Tools:** <named libraries / services with links>
- **Notebook:** [Explore the example](../notebook.md) <!-- Remove this line if the user story has no supporting notebook. -->
- **Status:** <span class="gks-status gks-status--production">production</span>

---

## The story

<2–4 paragraphs: the real situation, what was hard before, what GKM unlocked.>

## The data

<Real example payloads, lightly annotated. Reference files in `./payloads/` where helpful. Snippet paths are repo-root-relative (the `base_path: ["."]` documentation configuration enables this):>

```json
--8<-- "docs/user-stories/<source>/<slug>/payloads/example.vrs.json"
```

## The tools used

<Concrete library/service names with versions and links. No vague references like "various tools".>

## Explore the example

When this user story has a supporting notebook, link to it here:

[**Explore the example**](../notebook.md)

If there is no supporting notebook, remove both this section and the
**Notebook** entry from **At a glance**.

## How to reuse this pattern

- [Product Quick Start Guide for X](https://link.to/product/quickstart)
- Related vignette: [<title>](../<other-slug>/vignette.md)
- Similar implementer: <name + link>

## Add a supporting notebook walkthrough

When a vignette has an executable example, keep the narrative and the notebook
on separate pages. Add the notebook under `notebooks/<source>/`, then register
its source and generated page in `scripts/gen_notebook_files.py`, placing the
generated page alongside the vignette at
`user-stories/<source>/<slug>/notebook.md`. Add the generated page as a nested
entry under the vignette in `zensical.toml`, add its `path` to the optional
`notebook` frontmatter mapping, link to it from the vignette, and copy any
notebook-local images or data through the generator so the rendered page does
not depend on files outside `docs-build/`.
