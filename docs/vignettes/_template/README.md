# Vignette Authoring Guide

This folder contains the canonical template for a GKS Starter Kit vignette. Copy `vignette.md` into a new folder under `docs/vignettes/<your-slug>/` and fill it in.

## Workflow

1. Pick a kebab-case slug (e.g. `brca-exchange-vrs-cross-source`).
2. Create the folder: `docs/vignettes/<your-slug>/`.
3. Copy `vignette.md` from this folder into it.
4. (Optional) Add `payloads/` and `diagrams/` subfolders for example data and figures referenced from your vignette body.
5. Fill in the frontmatter (see field reference below) and the body sections.
6. Run `mkdocs build --strict` locally to confirm there are no broken links or YAML errors.
7. Open a PR. The PR template's checklist mirrors the requirements below.

## Frontmatter field reference

| Field | Required | Notes |
| ----- | -------- | ----- |
| `title` | yes | One-line use case description. Quoted. |
| `slug` | yes | Kebab-case. Must match the folder name. |
| `summary` | yes | One-sentence catalog blurb shown on the index card. Distinct from "Why this matters" in the body. |
| `products` | yes | List of `{name, version?}` entries. `name` must be one of: `VRS`, `Cat-VRS`, `VA-Spec`. Version is optional but strongly encouraged. |
| `pattern` | yes | One value from `docs/vignettes/patterns.yml`. If no existing pattern fits, add a new entry to `patterns.yml` in the same PR. |
| `implementer` | yes | The organization, consortium, knowledgebase, or project behind the use case. For `status: proposal`, the proposing party. |
| `status` | yes | One of: `production`, `pilot`, `proposal`. Rendered as a coloured badge on the index. |
| `contributors` | no | GitHub handles or names. Optional. |
| `last_updated` | yes | ISO date (`YYYY-MM-DD`). Drives the default catalog sort. |

## "Why this matters" — what good looks like

The first paragraph after the title is the **forwardable** part of your vignette. Someone should be able to paste it into Slack or an email to a non-technical decision-maker and have it stand on its own.

**Strong example** (concrete, plain-language, names the problem and the win):

> "BRCA Exchange pulls cancer-risk variants from many sources — ClinVar, gnomAD, LOVD, the literature. Each source describes the same variant differently, which makes it hard to know which entries are duplicates. By generating a single shared identifier for each variant from its underlying sequence change, the project can confidently deduplicate across sources and surface a complete, non-redundant view to clinicians and researchers."

**Weak example** (jargon, no audience awareness, no real-world stakes):

> "We apply VRS digests to harmonize variant identifiers across heterogeneous sources, enabling lossless cross-source deduplication via canonical content-addressed identification."

If you're not sure your paragraph passes the "would my boss understand this?" test, ask in your PR — a reviewer can help tune it.

## Naming new pattern values

If your vignette doesn't fit an existing pattern in `patterns.yml`, add a new entry in the same PR:

```yaml
# docs/vignettes/patterns.yml
your-new-pattern: Human-readable label for your pattern
```

Keep new pattern names broad enough to plausibly cover future vignettes — e.g. `cross-source-variant-harmonization` is better than `brca-exchange-deduplication`.

## See also

- [Contribution guide](../../contribute.md)
- [Pull-request template](https://github.com/ga4gh/gks-starter-kit/blob/main/.github/PULL_REQUEST_TEMPLATE.md)
