# Contribute

The GKM Starter Kit grows by community contribution. It has three pillars, with a contribution path for each. Pick the one that matches what you have to offer.

- **[Contribute a data bundle](#contribute-a-data-bundle)** — you have a resource whose knowledge you want to package and share.
- **[Contribute to `ga4gh.gkm`](#contribute-to-ga4ghgkm)** — you want to help build the GKM Python package that loads and works with bundles.
- **[Contribute a vignette](#contribute-a-vignette)** — you've built something real with GKM, or you're proposing to.

---

## Contribute a data bundle

If your resource produces genomic knowledge, such as variant classifications, evidence, or categorical variants, you can package it as a **GKM bundle**: a shareable document composed from the modular GKM schemas so others can consume it with common semantics.

**Is it a fit?** Your resource has real knowledge to share, and you can express it against the GKM schemas (GKS-Core, VRS, Cat-VRS, VA-Spec).

**How to start:** Read the [Data Bundles overview](data/index.md) to see the packaging pattern and the partner model. To propose a bundle from your resource, open an issue and a maintainer will help you scope its producer-specific format.

---

## Contribute to `ga4gh.gkm`

The **GKM Python package, `ga4gh.gkm`,** provides a lightweight layer that
loads bundles into in-memory GKM objects, lets you explore and manipulate them,
and writes them back to the producer's JSON format.

**Status: active development.** See the [Python package overview](library/index.md) for the current load → explore → export workflow and planned extension points. If you'd like to help shape the package, open an issue to start the conversation.

---

## Contribute a vignette

If you've built something real on top of GKS, or you're proposing to, a vignette is the way to share it.

### Is your idea a fit?

Use this short checklist:

- [ ] Real implementation, or a credible proposal with a clear use case.
- [ ] Uses one or more GKM standards (GKS-Core, VRS, Cat-VRS, VA-Spec).
- [ ] You can include real data (example payloads, not synthetic placeholders).
- [ ] You can name the actual tools and libraries used, with versions and links.
- [ ] The value can be stated in plain language that a non-technical reader could understand and forward.

If all five are yes, you have a vignette. If you're not sure, open an issue (see below) and a maintainer will help.

### Two ways to contribute

#### 1. Propose first (lower commitment)

Open an issue using the [**Propose a vignette**](https://github.com/ga4gh/gks-starter-kit/issues/new?template=propose-vignette.yml) template. The form captures the title, implementer, products, a one-paragraph use case, status, and your contact. A maintainer will triage and either assign it back to you or to a willing helper.

#### 2. Draft a PR directly

If you're ready to write:

1. Read the [vignette authoring guide](https://github.com/ga4gh/gks-starter-kit/tree/main/docs/vignettes/_template) (the `_template/` folder in the repo).
2. Copy `docs/vignettes/_template/vignette.md` into a new `docs/vignettes/<your-slug>/` folder.
3. Fill in the frontmatter and body. Add `payloads/` and `diagrams/` subfolders as needed.
4. Run `mkdocs build --strict` locally to catch errors.
5. Open a PR. The PR template's checklist mirrors the authoring requirements.

### What makes a strong vignette

- The "Why this matters" paragraph uses plain language with no unexplained jargon.
- Payloads are real (or, if synthetic, clearly labelled).
- Tools are named explicitly with versions and links.
- The `status` field accurately reflects where the implementation actually is.
- A new pattern, if you need one, is added to `docs/vignettes/patterns.yml` in the same PR.

The [vignette authoring guide](https://github.com/ga4gh/gks-starter-kit/tree/main/docs/vignettes/_template) has examples of strong and weak "Why this matters" paragraphs. It is worth reading before you start.

### What to expect from review

A maintainer will review against the template. They may ask for clarifications, most often on the "Why this matters" paragraph (plain language is harder than it looks) or on confirming the `status` matches reality. Once aligned, the vignette merges and ships on the next push.
