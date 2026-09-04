# Contribute to User Stories

If you've built something real on top of GKS, or you're proposing to, a user story is the way to share it.

## Is your idea a fit?

Use this short checklist:

- [ ] Real implementation, or a credible proposal with a clear use case.
- [ ] Uses one or more GKM standards (GKM-Core, VRS, Cat-VRS, VA-Spec).
- [ ] You can include real data (example payloads, not synthetic placeholders).
- [ ] You can name the actual tools and libraries used, with versions and links.
- [ ] The value can be stated in plain language that a non-technical reader could understand and forward.

If all five are yes, you have a user story. If you're not sure, open an issue (see below) and a maintainer will help.

## Two ways to contribute

### 1. Propose first (lower commitment)

Open an issue using the [**Propose a user story**](https://github.com/ga4gh/gkm-starter-kit/issues/new?template=propose-vignette.yml) template. The form captures the title, implementer, products, a one-paragraph use case, status, and your contact. A maintainer will triage and either assign it back to you or to a willing helper.

### 2. Draft a PR directly

If you're ready to write:

1. Read the [user story authoring guide](https://github.com/ga4gh/gkm-starter-kit/tree/main/docs/vignettes/_template) (the `_template/` folder in the repo).
2. Copy `docs/vignettes/_template/vignette.md` into a new `docs/vignettes/<your-slug>/` folder.
3. Fill in the frontmatter and body. Add `payloads/` and `diagrams/` subfolders as needed.
4. Run `mkdocs build --strict` locally to catch errors.
5. Open a PR. The PR template's checklist mirrors the authoring requirements.

## What makes a strong user story

- The "Why this matters" paragraph uses plain language with no unexplained jargon.
- Payloads are real (or, if synthetic, clearly labelled).
- Tools are named explicitly with versions and links.
- The `status` field accurately reflects where the implementation actually is.
- A new pattern, if you need one, is added to `docs/vignettes/patterns.yml` in the same PR.

The [user story authoring guide](https://github.com/ga4gh/gkm-starter-kit/tree/main/docs/vignettes/_template) has examples of strong and weak "Why this matters" paragraphs. It is worth reading before you start.

## What to expect from review

A maintainer will review against the template. They may ask for clarifications, most often on the "Why this matters" paragraph (plain language is harder than it looks) or on confirming the `status` matches reality. Once aligned, the user story merges and ships on the next push.
