---
title: "<One-line use case>"
slug: <kebab-case-slug-matching-folder-name>
summary: "<One-sentence catalog blurb. Distinct from 'Why this matters' below.>"
products:
  - name: VRS              # one of: VRS, Cat-VRS, VA-Spec
    version: "2.0"         # optional but strongly encouraged
pattern: <one value from docs/vignettes/patterns.yml>
implementer: <organization, consortium, knowledgebase, or project>
status: production         # one of: production | pilot | proposal
contributors:
  - <GitHub handle or name>
last_updated: 2026-05-27
---

# <Your one-line use case — the title as it should appear in the rendered page (match the `title` frontmatter field above)>

**Why this matters**

<3–5 sentence plain-language paragraph. This is the forwardable bit — written so a non-technical reader could quote it. No jargon, no acronyms without expansion.>

**At a glance**

- **Who:** <implementer>
- **GKS products used:** <product + version per entry, e.g. VRS 2.0, VA-Spec 1.0>
- **Tools:** <named libraries / services with links>
- **Status:** <production | pilot | proposal>

---

## The story

<2–4 paragraphs: the real situation, what was hard before, what GKS unlocked.>

## The data

<Real example payloads, lightly annotated. Reference files in `./payloads/` where helpful. Snippet paths are repo-root-relative (the `base_path: ["."]` config in `mkdocs.yml` enables this):>

```json
--8<-- "docs/vignettes/<slug>/payloads/example.vrs.json"
```

## The tools used

<Concrete library/service names with versions and links. No vague references like "various tools".>

## How to reuse this pattern

- [Product Quick Start Guide for X](https://link.to/product/quickstart)
- Related vignette: [<title>](../<other-slug>/vignette.md)
- Similar implementer: <name + link>
