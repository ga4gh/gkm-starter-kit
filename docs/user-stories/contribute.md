# Contribute to User Stories

Share a user story if you have built on GKS or have a credible proposal.

## Is your idea a fit?

Your story should:

- [ ] Describe a real implementation or a credible proposal with a clear use case.
- [ ] Use one or more GKS standards: GKS-Core, VRS, Cat-VRS, or VA-Spec.
- [ ] Include real example payloads, or clearly label synthetic payloads.
- [ ] Name the tools and libraries used, with their own versions and links.
- [ ] State the value in plain language that a non-technical reader can understand and forward.

If you are unsure, open an issue and a maintainer can help.

## Two ways to contribute

### 1. Propose first (lower commitment)

Open an issue using the [**Propose a user story**](https://github.com/ga4gh/gkm-starter-kit/issues/new?template=propose-vignette.yml) form. It collects the title, source namespace, slug, catalog summary, implementer, GKS products and specification versions, reuse pattern, plain-language rationale, status, tools, and relevant links. A maintainer will triage the proposal and help determine the next step.

### 2. Draft a PR directly

To draft a PR:

1. Read the [user story authoring guide](https://github.com/ga4gh/gkm-starter-kit/tree/main/docs/user-stories/_template) (the `_template/` folder in the repo).
2. Copy `docs/user-stories/_template/vignette.md` into a new `docs/user-stories/<source>/<your-slug>/` folder.
3. Fill in the frontmatter and body. Add `payloads/` and `diagrams/` subfolders as needed.
4. Run `python -m scripts.build_docs && zensical build --clean --strict` locally.
5. Open a PR. The PR template's checklist mirrors the authoring requirements.

## What makes a strong user story

- The "Why this matters" paragraph uses plain language with no unexplained jargon or acronyms.
- Payloads are real, or synthetic payloads are clearly labelled.
- Tools are named explicitly with their own versions and links. Record GKS specification versions separately in `products`.
- The `status` field accurately reflects where the implementation actually is.
- A new `pattern` value is added to `docs/user-stories/patterns.yml` in the same PR when needed.

Read the [user story authoring guide](https://github.com/ga4gh/gkm-starter-kit/tree/main/docs/user-stories/_template) before drafting. It defines all frontmatter fields and includes strong and weak "Why this matters" examples.

## What to expect from review

A maintainer reviews each story against the template. They may ask you to clarify the plain-language rationale or confirm the `status`. Merged stories publish on the next push.
