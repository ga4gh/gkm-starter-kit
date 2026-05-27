# GKS Starter Kit — v1 Design

**Date:** 2026-05-27
**Status:** Draft for review
**Repo:** `gks-starter-kit` (local at `/Users/lbabb/Development/gks/gks-starter-kit`; not yet pushed to GitHub)

## 1. Context

The Genomic Knowledge Standards (GKS) ecosystem under GA4GH includes multiple products (VRS, Cat-VRS, VA-Spec, and others). At the 2026-04-17 GKS Roadmap session, Alex proposed a single community-facing resource — the **Genomic Knowledge Starter Kit** — to give outside adopters one entry point into the ecosystem.

Feedback from Montreal Connect noted that current per-product documentation is theoretical and jargon-heavy. A complementary, narrative, share-friendly resource would help adopters carry the value proposition to their teams, leadership, and broader communities.

The Starter Kit is also intended to align with — not duplicate — the existing GA4GH Starter Kit model: a single ecosystem-level resource rather than a per-product proliferation of "starter kits."

## 2. Goals

In v1, this repo will provide:

1. **A library of vignettes** — clear, concise walk-throughs of high-value real-world uses of GKS, each including the actual data and tools needed to deliver the use case.
2. **A tiered narrative shape per vignette** so a single artifact serves both the technical implementer reading it and the non-technical stakeholder it may be forwarded to.
3. **A discoverable, browsable catalog** designed for ~12 vignettes over time, filterable by GKS product, use-case pattern, and implementer.
4. **A low-friction contribution path** that lets the GKS community recruit and submit vignettes via issue or PR.
5. **A small orientation surface** — landing, About — that frames the resource and links out to product Quick Start Guides and the GA4GH Starter Kit.

## 3. Non-goals (v1)

The following are explicitly **deferred to a later milestone**, not built in v1:

- A structured live-implementer registry (separate from the vignettes themselves).
- A Python toolkit for consuming data from implementers.
- Full ecosystem orientation / product-routing pages beyond a single About page.

The following are **permanently out of scope** for this repo:

- Per-product Quick Start Guides or Implementation Guides. These belong in each GKS product's own ReadTheDocs site. This repo links *out* to them; it does not absorb them. The term "Starter Kit" is reserved for this GKS-level resource.
- Spec-internal documentation.
- The forthcoming GKS Home Page itself. This repo's content will be referenced from the Home Page when it lands; it is not the Home Page.

## 4. v1 deliverable summary

A published mkdocs Material site (on GitHub Pages) containing:

- `docs/index.md` — landing
- `docs/about.md` — 1-page "what is GKS" + relationship to product Quick Starts and the GA4GH Starter Kit
- `docs/contribute.md` — contribution guide
- `docs/vignettes/index.md` — browsable catalog
- `docs/vignettes/_template/` — canonical template + authoring guide
- `docs/vignettes/brca-exchange-vrs-cross-source/` — one polished worked-example vignette (BRCA Exchange + VRS for cross-source variant deduplication)
- GitHub issue + PR templates supporting the contribution flow
- A GitHub Action that builds and publishes the site to `gh-pages` on push to `main`

## 5. Repo & site layout

```
gks-starter-kit/
├── README.md                       # GitHub-facing; brief, points to rendered site
├── LICENSE
├── mkdocs.yml                      # site config: Material theme, nav, plugins
├── pyproject.toml                  # docs build dependencies only (no app code)
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── propose-vignette.yml    # structured "I want to contribute a vignette" form
│   ├── PULL_REQUEST_TEMPLATE.md    # checklist tied to vignette template
│   └── workflows/
│       └── publish.yml             # build + deploy to gh-pages on push to main
└── docs/
    ├── index.md                    # landing
    ├── about.md                    # orientation
    ├── contribute.md               # contribution guide
    ├── vignettes/
    │   ├── index.md                # browsable catalog
    │   ├── patterns.yml            # controlled vocabulary of use-case patterns
    │   ├── _template/
    │   │   ├── vignette.md         # canonical template, copy-to-create
    │   │   └── README.md           # authoring guide for contributors
    │   └── brca-exchange-vrs-cross-source/
    │       ├── vignette.md
    │       ├── payloads/
    │       │   └── brca1-variant.vrs.json
    │       └── diagrams/
    │           └── pipeline.svg
    └── assets/
        ├── css/extra.css           # small theming touches (status badge colours, etc.)
        └── img/                    # shared imagery
```

**Site navigation (`mkdocs.yml`):** Home · Vignettes · Contribute · About. The Vignettes section expands to individual vignettes; the `_template/` folder is excluded from nav.

**Conventions:**

- Vignette folder names are kebab-case slugs matching the vignette's `slug` frontmatter field. No date prefixes — vignettes are not time-ordered.
- The `_template/` leading underscore both signals "not a real vignette" and helps the mkdocs nav exclusion rule.
- No application code in v1. `pyproject.toml` carries only docs-build dependencies (mkdocs-material plus any plugins).

## 6. Vignette format

### 6.1 File layout

Every vignette lives in `docs/vignettes/<slug>/` and consists of:

- `vignette.md` — required. The narrative file with frontmatter + body.
- `payloads/` — optional. Real example data referenced from the vignette body (JSON, YAML, VCF snippets, etc.).
- `diagrams/` — optional. SVG or PNG diagrams referenced from the vignette body.

### 6.2 Frontmatter schema

```yaml
title: "BRCA Exchange: identifying unique variants across sources with VRS"
slug: brca-exchange-vrs-cross-source           # matches folder name
summary: "Using VRS digests to deduplicate BRCA variants pulled from ClinVar, gnomAD, LOVD, and the literature."
products:                                       # at least one entry required
  - name: VRS                                   # enum: VRS, Cat-VRS, VA-Spec (extensible)
    version: "2.0"                              # optional but strongly encouraged
pattern: cross-source-variant-harmonization     # one value from patterns.yml
implementer: BRCA Exchange                      # implementer / source organization or project
status: production                              # enum: production | pilot | proposal
contributors: ["…"]                             # optional, GitHub handles or names
last_updated: 2026-05-27                        # ISO date
```

**Field semantics:**

- `products`: list of `{name, version?}` objects. `name` is drawn from a small extensible enum of GKS product names. `version` is optional but strongly encouraged — vignettes that span versions may omit it.
- `pattern`: a single value from `docs/vignettes/patterns.yml`. New patterns are added via PR alongside the vignette that introduces them.
- `implementer`: the organization, consortium, knowledgebase, or project behind the vignette. For `status: proposal` vignettes, this is the proposing party.
- `status`: rendered as a coloured badge on the index card (production = green, pilot = amber, proposal = grey).
- `summary`: one-line catalog blurb, distinct from the body's "Why this matters" paragraph.

**Initial `patterns.yml` seed values** (the vocabulary grows by PR):

- `cross-source-variant-harmonization`
- `knowledgebase-exchange`
- `variant-categorization`
- `variant-annotation`
- `clinical-evidence-sharing`

### 6.3 Body structure

```markdown
# {{ title }}

**Why this matters**
<3–5 sentence plain-language paragraph. The forwardable bit — written so
a non-technical reader could quote it. No jargon, no acronyms without
expansion.>

**At a glance**
- **Who:** {{ implementer }}
- **GKS products used:** <product + version per entry, e.g. VRS 2.0, VA-Spec 1.0>
- **Tools:** <named libraries / services with links>
- **Status:** {{ status }}

---

## The story
<2–4 paragraphs: the real situation, what was hard before, what GKS unlocked.>

## The data
<Real example payloads, lightly annotated. Pull from ./payloads/ where helpful.>

## The tools used
<Concrete library/service names with versions + links. No vague references.>

## How to reuse this pattern
<Outbound links: product Quick Start Guides, related vignettes, similar implementers.>
```

### 6.4 Authoring guide (`docs/vignettes/_template/README.md`)

A short guide aimed at contributors. Contents:

- How to copy the template into a new vignette folder.
- Field-by-field explanation of the frontmatter schema with examples of correct values.
- Examples of strong vs. weak "Why this matters" paragraphs (the most-failed section in practice).
- How to add a new value to `patterns.yml` if no existing pattern fits.
- Pointers to the contribution guide (`docs/contribute.md`) and PR template.

## 7. Reader-facing pages

### 7.1 Landing — `docs/index.md`

A thin doorway. Contents:

- Resource name + tagline (e.g. "Real-world walk-throughs of high-value uses of the GA4GH Genomic Knowledge Standards").
- A 2-sentence framing: who this is for and what they'll find.
- A prominent **Browse vignettes →** call to action linking to the catalog.
- Secondary links to *Contribute* and *About*.

No additional explanatory content on the landing — its job is to route.

### 7.2 Vignette catalog — `docs/vignettes/index.md`

The browsable library. Contents in order:

1. One-line intro framing what readers are looking at.
2. **Filter chips** for the three browse axes: products, patterns, implementers. Clicking a chip narrows the visible list.
3. **Vignette cards** — one per vignette. Each card displays:
   - Title (linked) and a coloured status badge.
   - Implementer and GKS products (with versions) as small tags.
   - The `summary` one-liner from frontmatter.
   - A "Read →" link to the vignette.
4. **Default sort:** reverse-chronological by `last_updated`.

**Implementation note (not part of the spec, but for the plan):** filtering is driven off frontmatter, likely using the mkdocs Material `tags` plugin plus a small custom index template. The exact mechanism is an implementation-plan choice; the spec requires only that the three filter axes work and the cards render as described.

### 7.3 About — `docs/about.md`

Three short sections:

1. **What is GKS** — one plain-language paragraph. Concrete examples of what the standards do, no jargon.
2. **What this Starter Kit is (and isn't)** — one paragraph framing the vignette library as the entry point, and explicitly stating that per-product onboarding lives in each product's own Quick Start Guide (with links).
3. **Where else to look** — labeled link list:
   - GA4GH Starter Kit (sibling, broader scope).
   - Each GKS product's Quick Start Guide / documentation site.
   - Spec sites for full technical reference.
   - GKS Home Page (link added once it lands).

## 8. Contribution flow

The recruit-from-community model requires that contributing be low-friction. Two entry paths, both ending in a PR.

### 8.1 Path 1 — Propose first

A contributor opens a GitHub Issue via `.github/ISSUE_TEMPLATE/propose-vignette.yml`. The form captures:

- Working title
- Implementer
- GKS products + versions
- One-paragraph use case
- Status (production / pilot / proposal)
- Contact / GitHub handle

A maintainer triages, confirms scope fit, and either assigns the issue back to the proposer or to a willing helper. Recommended for contributors who aren't sure their idea fits.

### 8.2 Path 2 — Draft directly

A contributor copies `docs/vignettes/_template/vignette.md` into a new `docs/vignettes/<slug>/` folder, fills it in following the authoring guide, and opens a PR.

### 8.3 Contribution guide — `docs/contribute.md`

Walks readers through both paths. Contents in order:

1. **Is your idea a fit?** — short checklist:
   - Is there a real implementation, or a credible proposal?
   - Does it use one or more GKS products?
   - Can you include real data and named tools?
   - Can the value be stated in plain language?
2. **Two ways to contribute** — the issue path and the PR path, with links.
3. **What makes a strong vignette** — short bullet list lifted from the authoring guide.
4. **Review and merge** — what to expect from maintainer review.

### 8.4 PR template — `.github/PULL_REQUEST_TEMPLATE.md`

A tight checklist:

- [ ] Frontmatter complete (`title`, `slug`, `summary`, `products`, `pattern`, `implementer`, `status`, `last_updated`)
- [ ] "Why this matters" reads in plain language, no unexplained jargon
- [ ] Real payloads under `payloads/` (no synthetic data unless explicitly labelled)
- [ ] Tools named with versions and links
- [ ] `status` matches reality
- [ ] If introducing a new `pattern`, value added to `docs/vignettes/patterns.yml` in the same PR

### 8.5 Maintainer governance (v1)

A short `MAINTAINERS.md` at the repo root names 1–2 reviewers responsible for triaging issues and reviewing PRs. The named maintainer(s) are identified and added before the repo is published publicly; the spec requires their presence but does not pre-assign individuals.

New pattern values go in via the same PR as the vignette that introduces them. No separate vocabulary RFC process in v1.

## 9. Technical setup

- **Site generator:** mkdocs with the Material theme.
- **Hosting:** GitHub Pages, deployed from a `gh-pages` branch.
- **Build/deploy:** GitHub Action runs on push to `main`, builds with `mkdocs build --strict`, deploys with `mkdocs gh-deploy --force` (or equivalent action).
- **Dependencies:** declared in `pyproject.toml`. At minimum: `mkdocs`, `mkdocs-material`. Additional plugins (e.g. `mkdocs-material[imaging]` for social cards, a tags/index plugin) are added by the implementation plan as needed.
- **Theme customization:** kept minimal in v1. Status-badge colours via `docs/assets/css/extra.css`. No custom JavaScript unless required for the filter UI.

## 10. Acceptance criteria for v1

The v1 milestone is complete when:

1. The site is published to GitHub Pages and reachable at a stable URL.
2. The four top-level pages (Home, About, Contribute, Vignettes index) render correctly.
3. The BRCA Exchange + VRS worked-example vignette exists with:
   - Complete frontmatter conforming to §6.2.
   - A "Why this matters" paragraph that meets the plain-language bar.
   - At least one real VRS payload under `payloads/`.
   - Named tools with versions and links (specific tool names confirmed with BRCA Exchange or via published BRCA Exchange documentation).
   - A `status` value that reflects BRCA Exchange's actual position on the workflow.
4. The vignette index supports filter chips for the three browse axes and displays the worked example as a card per §7.2.
5. The contribution path is exercisable end-to-end: a new contributor can open the issue form, or copy the template and open a PR, with the PR-template checklist appearing.
6. `MAINTAINERS.md` names at least one maintainer.
7. The `mkdocs build --strict` build passes in CI on push to `main`.

## 11. Open questions for maintainer follow-up

These do not block design approval but must be resolved during implementation:

- Who is the named v1 maintainer in `MAINTAINERS.md`?
- What is BRCA Exchange's actual `status` on the cross-source VRS workflow? (production / pilot / proposal)
- Which specific tools (e.g. `vrs-python` version) does BRCA Exchange use for VRS digest generation, and what links should the vignette point to?
- What is the canonical site URL (e.g. `gks.github.io/gks-starter-kit` vs a custom domain)?

## 12. Architecture notes

The repo is documentation, not application code, so "architecture" largely reduces to file-layout and content-contract concerns:

- **Vignette folder** is the unit of content. Each is independently understandable (a reader can land on a single vignette and get value without reading any other page) and independently authorable (a contributor can create one without coordinating with other vignettes).
- **`patterns.yml`** is the single source of truth for the use-case-pattern vocabulary. Vignettes reference it; the index page reads it; PRs that introduce a new pattern modify it. Centralizing it here prevents pattern drift across vignettes.
- **Frontmatter schema** is the content contract between authors, the index renderer, and any future tooling. Changes to it are breaking and require updating the template, the authoring guide, and any rendered index logic together.
- **`_template/`** is the canonical source for the vignette structure. Authors copy from it; reviewers check against it. Changing the template is a v1.x concern; v1 ships with the template defined in §6.3.

## 13. What's explicitly NOT in this spec

- The full content of any vignette beyond the BRCA Exchange worked example.
- The exact plugin choice for the filterable index (left to the implementation plan).
- Visual/brand polish beyond minimum theming (custom logo, social card design, etc.).
- The implementer registry, Python toolkit, and broader ecosystem-orientation pages (all deferred per §3).
