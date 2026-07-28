# GKS Starter Kit v2 (Approach C) — Site Reorganization Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the GKS Starter Kit documentation site from a vignette-only site into the **three-pillar** structure using **Approach C (value-driven landing + pillar-structured nav)**. Deliver: a persuasion-first landing page that tells the value story and routes two audiences; three durable top-level sections named for what they are — **Data Bundles** (Pillar 1), **Python Package** (Pillar 2), **Vignettes** (Pillar 3); the site tooling proven out in the POC (`pymdownx.inlinehilite`, `pymdownx.tabbed`, `json-schema-for-humans`); and a reframed About + per-pillar Contribute.

**Scope boundary (read first):** This plan reorganizes the *site* and creates the *homes* for all three pillars. It does **not** build the Pillar 2 Python package itself, nor the `CustomProposition` object — those are separate spec → plan cycles. Where this plan creates Pillar 2 / Pillar 3 content, it creates **overview pages + one seed/worked example**, with explicit "future work" markers pointing at the deferred efforts. The existing BRCA Exchange vignette and its catalog machinery are preserved, moved under the Vignettes (Pillar 3) section unchanged.

**Architecture:** Static documentation site (unchanged engine). Markdown in `docs/`, rendered by mkdocs + Material, published to GitHub Pages via the existing `.github/workflows/publish.yml`. The v1 catalog machinery (`mkdocs-macros-plugin` + `mkdocs-gen-files` + `scripts/vignette_loader.py`) is retained and continues to drive the Vignettes section. Pillar 1 adds a **build-time JSON-Schema rendering step**: `json-schema-for-humans` converts a source schema into Markdown that `mkdocs-gen-files` emits as a browsable page. `mkdocs build --strict` remains the regression gate.

**Tech Stack:** Python 3.11+, mkdocs 1.6.1, mkdocs-material 9.5.49, mkdocs-macros-plugin 1.3.7, mkdocs-gen-files 0.5.0, pymdown-extensions 10.21.3 (already installed; `inlinehilite` + `tabbed` newly *enabled*), json-schema-for-humans 1.5.1 (**new dependency**), PyYAML, GitHub Actions, GitHub Pages.

**Design source:** The Approach C design decided in the v2 brainstorming session (2026-07-27). A standalone spec doc is **not** a prerequisite for this plan; the design summary below is the contract. (If a spec is later written, link it here.)

---

## Design summary (the contract this plan implements)

The reframing (2026 GA4GH Spring Connect; Alan Rubin's "an engineering team lead can't quickly see the value" problem) recasts the Starter Kit around a single claim: *the GKS reference libraries let you create and validate knowledge objects, but say nothing about how you collect, make interoperable, share, and consume that knowledge — the Starter Kit demonstrates that missing layer.* Three pillars carry the arc:

- **Pillar 1 — Packaged data (`Data Bundles`):** real content from community partners (ClinVar GKS, CIViC) composed from modular GKS schemas into larger bundle documents; possibly live-service *registration* for very large datasets (gnomAD, ClinVar GKS) rather than downloads.
- **Pillar 2 — Python package (`Python Package`):** lightweight code on top of the reference libraries that *loads* bundles into in-memory GKS objects, lets you explore/manipulate them, and *exports* back to GKS JSON.
- **Pillar 3 — Vignettes (`Vignettes`):** real community use cases; may build on Pillars 1–2 or not (e.g. reclassification within a single resource). The through-line: "what a group needs the standards for, and the standards delivering it."

**Approach C decisions:**

1. **Landing does the persuasion job** (no longer a thin doorway): value narrative + a **pipeline visual** (`data → library → use case`) + **audience routing** ("I lead a team" / "I want to build" / "I have data to share"). The landing embeds the **four-altitude content-tabs demo** (narrative ↔ GKS JSON ↔ Python ↔ schema) as its proof centerpiece.
2. **Durable nav is pillar-structured but named for what each section IS** — never "Pillar N". Nav order preserves the pipeline left-to-right: **Home · Data Bundles · Python Package · Vignettes · Contribute · About**.
3. **Site tooling** (validated in the POC): enable `pymdownx.inlinehilite` and `pymdownx.tabbed` (with `alternate_style: true`); adopt `json-schema-for-humans` rendered via `mkdocs-gen-files` for Pillar 1 schema pages.
4. **Contribute becomes per-pillar** (contribute a bundle / contribute to the library / contribute a vignette).
5. **Dual audience** (scientist + engineering lead) is served by the content-tabs "multiple altitudes on one page" pattern rather than by splitting into separate pages.

**Hermeticity note (Pillar 1 schema rendering):** `json-schema-for-humans` can follow `$ref`s. The real GKS bundle schema uses **remote `https://w3id.org/ga4gh/...` `$ref`s** (see `docs/superpowers/plans/example.jsonc`). Resolving those at build time is a network + reproducibility risk and would break offline/CI-pinned builds. **v2 decision:** render a **self-contained** bundle schema (local `$defs`, no remote `$ref`s) for the demonstrator page. Live rendering of the fully remote-`$ref`-composed schema is deferred as a future enhancement.

---

## How to verify a docs project (TDD adaptation)

Same adaptation as the v1 plan:

- **The "failing test" is** `mkdocs build --strict` failing, or a specific structural assertion failing (page missing, link broken, snippet not embedded, tab markup not rendered).
- **The "passing test"** is the same command succeeding plus a visual/structural check (`mkdocs serve` + browse, or `grep`/`test -f` against the built `site/`, or a headless screenshot).
- **Commit cadence:** verify before committing, one logical change per commit.

Use @superpowers:verification-before-completion to confirm each verification step actually ran and produced the expected output before claiming a task done. Use @superpowers:test-driven-development for the write-verification-first habit.

**Screenshot verification (optional but recommended for the landing + tabs):** the POC used headless Chrome:
```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --window-size=1300,1700 \
  --screenshot=/tmp/shot.png "file://$PWD/site/index.html"
```

---

## File Structure

Files this plan creates or modifies, with single-responsibility scope:

**Config & deps**
- `requirements.txt` — add `json-schema-for-humans==1.5.1`.
- `mkdocs.yml` — enable `inlinehilite` + `tabbed`; restructure `nav` to the three-pillar layout; register the new schema-generation gen-files script; update `exclude_docs` for any new source-only files.

**Landing & orientation**
- `docs/index.md` — rewritten landing (value narrative + pipeline visual + audience routing + embedded four-altitude content-tabs demo).
- `docs/about.md` — reframed around the three-pillar model.
- `docs/contribute.md` — reframed into three per-pillar contribution paths.
- `docs/assets/css/extra.css` — add styles for the pillar cards / audience-routing buttons / pipeline visual (extends existing `.gks-*` styles).

**Pillar 1 — Data Bundles**
- `docs/data/index.md` — Pillar 1 overview: what a GKS bundle is, the packaging pattern, partners (ClinVar GKS, CIViC), download-vs-register note; links to the rendered schema.
- `docs/data/schemas/gks-bundle.schema.json` — the self-contained demonstrator bundle schema (source of truth for the rendered page).
- `scripts/gen_schema_pages.py` — new gen-files script: runs `json-schema-for-humans` over `docs/data/schemas/*.schema.json` and emits `data/schemas/<name>.md` browsable pages at build time.

**Pillar 2 — Python Package**
- `docs/library/index.md` — Pillar 2 overview: what the package does (load → explore → export), how it sits on the reference libraries, status = "in development", links to the deferred spec. Uses content tabs to show a load/explore/export snippet.

**Pillar 3 — Vignettes (preserved, reframed)**
- `docs/vignettes/index.md` — intro reframed to position vignettes as Pillar 3 (may or may not build on Pillars 1–2). Catalog machinery unchanged.
- (existing `docs/vignettes/_template/`, `patterns.yml`, `brca-exchange-vrs-cross-source/`, `scripts/vignette_loader.py`, `main.py`, `scripts/gen_filter_pages.py` — unchanged.)

**Single-responsibility rationale:** `gen_schema_pages.py` is a *separate* gen-files script from `gen_filter_pages.py` because they render different content from different sources (schemas vs. vignette frontmatter) and will evolve independently. The demonstrator schema is a committed source file (not generated) so it is reviewable and diffable; only its *rendering* is generated.

## Worktree note

This modifies an existing published site. Recommend a feature branch (`v2-approach-c`) rather than committing to `main` directly, since the reorganization changes the live nav. If using worktrees per @superpowers:using-git-worktrees, create one for this branch. Merge to `main` only after the full-site `--strict` build + visual QA in the final chunk passes.

---

## Chunk 1: Tooling + nav restructure (buildable skeleton)

Enable the POC-validated extensions, add the schema-rendering dependency, and restructure the nav to the three-pillar layout with placeholder section pages. End state: `mkdocs build --strict` passes with the new nav and empty pillar sections.

### Task 1.1: Add the schema-rendering dependency

**Files:** Modify `requirements.txt`

- [ ] **Step 1: Verify current state** — `grep -n json-schema requirements.txt || echo "not present (expected)"`. Expected: not present.
- [ ] **Step 2:** Append `json-schema-for-humans==1.5.1` to `requirements.txt`.
- [ ] **Step 3:** Install into the existing venv: `./.venv/bin/pip install -r requirements.txt`. Expected: installs `json-schema-for-humans` and its deps (`dataclasses-json`, `markdown2`, …) without error.
- [ ] **Step 4:** Verify the CLI is present: `./.venv/bin/generate-schema-doc --help | head -1`. Expected: usage line printed.
- [ ] **Step 5: Commit** — `git add requirements.txt && git commit -m "Add json-schema-for-humans for Pillar 1 schema rendering"`.

### Task 1.2: Enable inlinehilite + tabbed and restructure nav

**Files:** Modify `mkdocs.yml`; create placeholder `docs/data/index.md`, `docs/library/index.md`.

- [ ] **Step 1: Write the failing verification** — the new sections don't exist yet, so a build with the new nav would fail. First create placeholders (Step 2), then wire nav (Step 3).
- [ ] **Step 2: Create placeholder section pages**

  `docs/data/index.md`:
  ```markdown
  # Data Bundles

  Placeholder for Pillar 1. Real overview lands in Chunk 3.
  ```
  `docs/library/index.md`:
  ```markdown
  # Python Package

  Placeholder for Pillar 2. Real overview lands in Chunk 4.
  ```

- [ ] **Step 3: Update `mkdocs.yml`** — add the two extensions to `markdown_extensions` (keep existing entries):

  ```yaml
  markdown_extensions:
    - admonition
    - attr_list
    - md_in_html
    - tables
    - pymdownx.details
    - pymdownx.superfences
    - pymdownx.inlinehilite            # NEW
    - pymdownx.highlight:              # NEW (pairs with inlinehilite; anchored line numbers)
        anchor_linenums: true
    - pymdownx.tabbed:                 # NEW — Material content tabs
        alternate_style: true
    - pymdownx.snippets:
        base_path: ["."]
        check_paths: true
  ```

  Add the tab-link theme feature (keep existing features):
  ```yaml
  theme:
    name: material
    features:
      - navigation.sections
      - navigation.expand
      - content.action.edit
      - content.code.copy
      - content.tabs.link             # NEW — sync tab selection across the page
  ```

  Replace the `nav` block with the three-pillar layout:
  ```yaml
  nav:
    - Home: index.md
    - Data Bundles:
        - data/index.md
    - Python Package:
        - library/index.md
    - Vignettes:
        - vignettes/index.md
    - Contribute: contribute.md
    - About: about.md
  ```

- [ ] **Step 4: Build** — `./.venv/bin/mkdocs build --strict`. Expected: exit 0.
- [ ] **Step 5: Confirm the new section pages built** —
  ```bash
  test -f site/data/index.html && echo OK
  test -f site/library/index.html && echo OK
  test -f site/vignettes/index.html && echo OK
  ```
  Expected: three `OK` lines.
- [ ] **Step 6: Commit** — `git add mkdocs.yml docs/data/index.md docs/library/index.md && git commit -m "Enable inlinehilite + tabbed; restructure nav to three pillars"`.

---

## Chunk 2: Value-driven landing page (Approach C centerpiece)

Rewrite `docs/index.md` from a thin doorway into the persuasion-first landing: value narrative, pipeline visual, audience routing, and the embedded four-altitude content-tabs demo.

### Task 2.1: Write the landing narrative + audience routing + pipeline

**Files:** Modify `docs/index.md`; modify `docs/assets/css/extra.css`.

- [ ] **Step 1: Replace `docs/index.md`** with (adjust prose as needed, keep the structure):

  ```markdown
  # GKS Starter Kit

  **The GA4GH Genomic Knowledge Standards let you create and validate genomic
  knowledge — from statements down through evidence. The Starter Kit shows you the
  part the specs leave out: how to _package_ that knowledge, _load and build_ with
  it, and _put it to work_ in real use cases.**

  Whether you lead an engineering team weighing adoption, or you're a scientist who
  needs the standards to do something concrete, this is the fastest way to see what
  GKS makes possible.

  ## How it fits together

  <div class="gks-pipeline" markdown>
  **📦 Data Bundles** → **🐍 Python Package** → **🔬 Vignettes**

  Packaged GKS data · loaded and manipulated in Python · demonstrated in real use cases
  </div>

  ## Start where you are

  <div class="grid cards" markdown>

  - :material-account-tie: **I lead a team**

      See the value fast — what GKS unlocks and why it makes your team's job easier.

      [Read a vignette →](vignettes/index.md)

  - :material-code-braces: **I want to build**

      Load real GKS data into Python objects, explore them, export them back.

      [Explore the Python package →](library/index.md)

  - :material-database: **I have data to share**

      Package your resource's knowledge as GKS bundles others can consume.

      [See the data bundles →](data/index.md)

  </div>

  ## See one object, four altitudes

  The same piece of genomic knowledge, shown at the level you care about — narrative
  for a scientist, JSON for a data engineer, Python for a developer, schema for an
  implementer. (This is the pattern used throughout the Starter Kit.)

  <!-- Four-altitude content-tabs demo embedded in Task 2.2 -->
  ```

- [ ] **Step 2: Add landing styles to `docs/assets/css/extra.css`** (append; do not remove existing `.gks-chip`/`.gks-status`):

  ```css
  /* v2 landing: pipeline strip */
  .gks-pipeline {
      padding: 1rem 1.25rem;
      border-radius: 0.5rem;
      background: var(--md-primary-fg-color--light);
      color: var(--md-primary-bg-color);
      text-align: center;
      font-size: 1.05rem;
  }
  .gks-pipeline strong { white-space: nowrap; }
  ```

  (The `grid cards` markup uses Material's built-in card grid — no custom CSS needed — which requires `attr_list` + `md_in_html`, both already enabled.)

- [ ] **Step 3: Confirm Material card-grid + icons prerequisites.** The `:material-*:` icons require Material's icon support (built in). The `grid cards` class is a Material feature. If icons render as literal text, verify `attr_list` and `md_in_html` are enabled (they are, from v1). No emoji-shortcode extension is required because literal emoji (📦🐍🔬) are used in the pipeline strip.
- [ ] **Step 4: Build** — `./.venv/bin/mkdocs build --strict`. Expected: exit 0.
- [ ] **Step 5: Verify content rendered** —
  ```bash
  grep -q "How it fits together" site/index.html && echo OK
  grep -q "gks-pipeline" site/index.html && echo OK
  grep -q "Start where you are" site/index.html && echo OK
  ```
  Expected: three `OK` lines.
- [ ] **Step 6: Commit** — `git add docs/index.md docs/assets/css/extra.css && git commit -m "Rewrite landing as value-driven three-pillar entry (Approach C)"`.

### Task 2.2: Embed the four-altitude content-tabs demo

**Files:** Modify `docs/index.md`.

- [ ] **Step 1:** Replace the `<!-- Four-altitude content-tabs demo embedded in Task 2.2 -->` comment with the content-tabs block (validated in the POC). Use a real BRCA1 example consistent with the existing vignette payload:

  ````markdown
  === "Narrative (scientist)"

      **BRCA1 c.68_69del is causal for hereditary breast-ovarian cancer syndrome.**
      A well-established pathogenic frameshift variant. The statement below *supports*
      that proposition; the direction and strength come from the submitting resource.

  === "GKS JSON (Pillar 1 bundle)"

      ```json
      {
        "bundleVersion": "1.0.0",
        "source": { "name": "ClinVar GKS", "url": "https://www.ncbi.nlm.nih.gov/clinvar/" },
        "statements": [{
          "id": "clinvar:SCV000000001",
          "direction": "supports",
          "proposition": {
            "type": "VariantPathogenicityProposition",
            "subject": { "id": "ga4gh:VA.abc123", "label": "BRCA1 c.68_69del" },
            "predicate": "isCausalFor",
            "object": { "id": "MONDO:0003582", "label": "hereditary breast-ovarian cancer syndrome" }
          }
        }]
      }
      ```

  === "Python (Pillar 2 library)"

      ```python
      from gks_kit import load                       # package name TBD — see Python Package section

      bundle = load("clinvar.gks.json")              # parse + validate
      stmt = bundle.statements[0]
      stmt.direction                                 # 'supports'
      stmt.proposition.predicate                     # 'isCausalFor'
      bundle.to_json("out.gks.json")                 # re-export canonical GKS JSON
      ```

  === "Schema (Pillar 1 contract)"

      The bundle validates against a JSON Schema composed from modular GKS `$ref`s.
      See the fully rendered, browsable schema under **[Data Bundles](data/index.md)**.
  ````

- [ ] **Step 2: Build** — `./.venv/bin/mkdocs build --strict`. Expected: exit 0.
- [ ] **Step 3: Verify the tab markup rendered (not literal `===`)** —
  ```bash
  grep -q 'class="tabbed-set' site/index.html && echo "OK: tabs rendered"
  grep -q "VariantPathogenicityProposition" site/index.html && echo "OK: JSON tab present"
  ! grep -q '=== "Narrative' site/index.html && echo "OK: no literal tab syntax leaked"
  ```
  Expected: three `OK` lines.
- [ ] **Step 4: Visual/screenshot check** — build, then headless-screenshot `site/index.html` (see verification preamble) and confirm the tab bar + pipeline strip + three audience cards render. Or `mkdocs serve` and click each tab.
- [ ] **Step 5: Commit** — `git add docs/index.md && git commit -m "Embed four-altitude content-tabs demo on landing"`.

---

## Chunk 3: Pillar 1 — Data Bundles section + rendered schema

Turn the placeholder into the Pillar 1 overview, add the self-contained demonstrator bundle schema, and wire the build-time schema-rendering gen-files script.

### Task 3.1: Add the demonstrator bundle schema

**Files:** Create `docs/data/schemas/gks-bundle.schema.json`.

- [ ] **Step 1:** Create the self-contained schema (local `$defs`, no remote `$ref`s — see hermeticity note). Use the POC schema as the basis: a `GksBundle` with `bundleVersion`, `source`, and `statements[] → Statement → Proposition (subject/predicate/object, type incl. CustomProposition example)`. (Copy from the POC at `scratchpad/poc/schema.json` if still present, or reconstruct per the design summary.)
- [ ] **Step 2: Verify it's valid JSON and valid JSON Schema** —
  ```bash
  ./.venv/bin/python -c "import json; json.load(open('docs/data/schemas/gks-bundle.schema.json')); print('valid JSON')"
  ./.venv/bin/generate-schema-doc --config template_name=md docs/data/schemas/gks-bundle.schema.json /tmp/_schema_probe.md && echo "renders OK"
  ```
  Expected: `valid JSON` then `renders OK`. Delete `/tmp/_schema_probe.md` after.
- [ ] **Step 3: Commit** — `git add docs/data/schemas/gks-bundle.schema.json && git commit -m "Add self-contained demonstrator GKS bundle schema"`.

### Task 3.2: Wire the schema-rendering gen-files script

**Files:** Create `scripts/gen_schema_pages.py`; modify `mkdocs.yml`.

- [ ] **Step 1: Create `scripts/gen_schema_pages.py`** — a gen-files script that renders every `docs/data/schemas/*.schema.json` to a browsable Markdown page at `data/schemas/<name>.md`:

  ```python
  """Render committed JSON Schemas to browsable Markdown at build time.

  For each docs/data/schemas/*.schema.json, run json-schema-for-humans (md
  template) and emit data/schemas/<name>.md via mkdocs-gen-files. Nothing lands
  on disk in docs/; the source schema files remain the reviewable source of truth.
  """

  from pathlib import Path
  import subprocess
  import sys

  import mkdocs_gen_files

  SCHEMA_DIR = Path("docs/data/schemas")

  def _render(schema_path: Path) -> str:
      # generate-schema-doc writes to a file; render to a temp path then read back.
      out = schema_path.with_suffix(".rendered.md")
      subprocess.run(
          [sys.executable, "-m", "json_schema_for_humans.generate",
           "--config", "template_name=md", "--config", "show_toc=true",
           str(schema_path), str(out)],
          check=True,
      )
      text = out.read_text(encoding="utf-8")
      out.unlink()
      return text

  for schema_path in sorted(SCHEMA_DIR.glob("*.schema.json")):
      name = schema_path.name.replace(".schema.json", "")
      rel = f"data/schemas/{name}.md"
      with mkdocs_gen_files.open(rel, "w") as f:
          f.write(_render(schema_path))
  ```

  **Note on invocation:** verify `python -m json_schema_for_humans.generate` is the correct module entrypoint in 1.5.1; if not, fall back to invoking the installed `generate-schema-doc` console script by absolute path, or import and call the library API (`json_schema_for_humans.generate.generate_from_file_object`). Confirm with:
  ```bash
  ./.venv/bin/python -c "import json_schema_for_humans.generate as g; print([x for x in dir(g) if 'generate' in x])"
  ```

- [ ] **Step 2: Register the script in `mkdocs.yml`** (add to the existing `gen-files` `scripts` list — do NOT replace the vignette filter script):
  ```yaml
  plugins:
    - search
    - macros:
        module_name: main
    - gen-files:
        scripts:
          - scripts/gen_filter_pages.py
          - scripts/gen_schema_pages.py     # NEW
  ```
- [ ] **Step 3: Add the rendered page to nav** (`mkdocs.yml` `nav`, under Data Bundles):
  ```yaml
    - Data Bundles:
        - data/index.md
        - Bundle schema: data/schemas/gks-bundle.md
  ```
- [ ] **Step 4: Build** — `./.venv/bin/mkdocs build --strict`. Expected: exit 0.
- [ ] **Step 5: Verify the schema page generated and rendered as tables (not raw JSON)** —
  ```bash
  test -f site/data/schemas/gks-bundle/index.html && echo "OK: page built"
  grep -q "GKS Bundle" site/data/schemas/gks-bundle/index.html && echo "OK: title"
  grep -q "VariantPathogenicityProposition\|CustomProposition" site/data/schemas/gks-bundle/index.html && echo "OK: $defs followed"
  ```
  Expected: three `OK` lines.
- [ ] **Step 6: Commit** — `git add scripts/gen_schema_pages.py mkdocs.yml && git commit -m "Render GKS bundle schema to a browsable page via gen-files"`.

### Task 3.3: Write the Pillar 1 overview page

**Files:** Modify `docs/data/index.md`.

- [ ] **Step 1:** Replace the placeholder with the overview: what a GKS bundle is and why it exists (packaging modular schemas into shareable documents with common semantics); the partner model (ClinVar GKS, CIViC); the **download-vs-register** consideration for very large datasets (gnomAD, ClinVar GKS); a link to the rendered **Bundle schema** page; and a short "what belongs here" note for contributors (points to the per-pillar Contribute path). Use an `admonition` for the download-vs-register tradeoff. Optionally use content tabs to show a trimmed bundle JSON next to its narrative.
- [ ] **Step 2: Build + verify** —
  ```bash
  ./.venv/bin/mkdocs build --strict
  grep -q "bundle" site/data/index.html && echo OK
  ```
  Expected: exit 0 and `OK`.
- [ ] **Step 3: Commit** — `git add docs/data/index.md && git commit -m "Write Pillar 1 Data Bundles overview"`.

---

## Chunk 4: Pillar 2 — Python Package overview (homes, not the library)

Turn the placeholder into the Pillar 2 overview. This describes the load → explore → export shape and marks the actual package + `CustomProposition` as in-development, linking to their deferred spec. **No library code is written here.**

### Task 4.1: Write the Pillar 2 overview page

**Files:** Modify `docs/library/index.md`.

- [ ] **Step 1:** Replace the placeholder with: the package's purpose (lightweight layer on `vrs-python` / `cat-vrs-python` / `va-spec-python` that loads Pillar 1 bundles into in-memory objects, lets you explore/manipulate, and exports back to GKS JSON); a **status admonition** (`type: note`) stating the package is in active design and linking to the forthcoming Pillar 2 spec/plan; and a **content-tabs** block showing the intended developer experience:

  ````markdown
  === "Load"
      ```python
      from gks_kit import load
      bundle = load("clinvar.gks.json")   # parse + validate against the bundle schema
      ```
  === "Explore"
      ```python
      for stmt in bundle.statements:
          print(stmt.proposition.predicate, "→", stmt.proposition.object["label"])
      ```
  === "Export"
      ```python
      bundle.to_json("out.gks.json")      # canonical GKS JSON
      ```
  ````

  Include a short **"Extending propositions"** paragraph that names `CustomProposition` as the planned pathway for statements on propositions GKS does not prescribe, marked as forthcoming and linked to its deferred spec. (Do not document a schema that does not exist yet — one paragraph of intent only.)

- [ ] **Step 2:** Use the literal package name placeholder `gks_kit` consistently, with a visible note that the final name is TBD, so a later rename is a single find/replace.
- [ ] **Step 3: Build + verify** —
  ```bash
  ./.venv/bin/mkdocs build --strict
  grep -q "class=\"tabbed-set" site/library/index.html && echo "OK: tabs render"
  grep -q "CustomProposition" site/library/index.html && echo "OK: extension pathway noted"
  ```
  Expected: exit 0 and two `OK` lines.
- [ ] **Step 4: Commit** — `git add docs/library/index.md && git commit -m "Write Pillar 2 Python Package overview (library build deferred)"`.

---

## Chunk 5: Pillar 3 — Vignettes reframing (preserve machinery)

Reposition the existing vignette catalog as Pillar 3. The catalog machinery, template, patterns vocabulary, and BRCA Exchange vignette are unchanged — only the framing intro is updated.

### Task 5.1: Reframe the vignettes index intro

**Files:** Modify `docs/vignettes/index.md` (intro prose only — leave the macros/Jinja catalog block untouched).

- [ ] **Step 1:** Update only the intro paragraph(s) above `{% set vignettes = list_vignettes() %}` to position vignettes as Pillar 3: real community use cases that **may or may not** build on Pillars 1–2 (e.g. reclassification within a single resource), with the common thread being "what a group needs the standards for, and the standards delivering it." Add one sentence linking back to Data Bundles / Python Package for vignettes that do build on them.
- [ ] **Step 2: Build + verify the catalog still renders** —
  ```bash
  ./.venv/bin/mkdocs build --strict
  grep -q "BRCA Exchange" site/vignettes/index.html && echo "OK: existing vignette still catalogued"
  test -d site/vignettes/by-pattern/cross-source-variant-harmonization && echo "OK: filter pages intact"
  ```
  Expected: exit 0 and two `OK` lines (proves the Jinja/macros block was not broken by the intro edit).
- [ ] **Step 3: Commit** — `git add docs/vignettes/index.md && git commit -m "Reframe vignettes as Pillar 3"`.

---

## Chunk 6: About + per-pillar Contribute + final QA

Reframe the orientation pages around the three pillars, and run a whole-site strict build + visual QA gate before merge.

### Task 6.1: Reframe the About page

**Files:** Modify `docs/about.md`.

- [ ] **Step 1:** Rework "What this Starter Kit is (and isn't)" to describe the three-pillar model and the "missing layer" framing (collect / make interoperable / share / consume), while preserving the existing "What is GKS?" paragraph and the "Where else to look" link list. Keep the explicit boundary that per-product onboarding lives in each product's Quick Start Guide (Starter Kit terminology rule).
- [ ] **Step 2: Build + verify** — `./.venv/bin/mkdocs build --strict && grep -q "three" site/about/index.html && echo OK` (adjust grep to actual wording). Expected: exit 0 and `OK`.
- [ ] **Step 3: Commit** — `git add docs/about.md && git commit -m "Reframe About around the three pillars"`.

### Task 6.2: Rework Contribute into per-pillar paths

**Files:** Modify `docs/contribute.md`.

- [ ] **Step 1:** Restructure into three contribution paths, each with its own short "is it a fit / how to" block:
  1. **Contribute a data bundle (Pillar 1)** — for resources packaging their knowledge; points at the bundle schema and the data section.
  2. **Contribute to the Python package (Pillar 2)** — marked as opening once the package spec lands; for now, links to the deferred spec / issue tracker.
  3. **Contribute a vignette (Pillar 3)** — the existing vignette path, preserved (issue template + PR path + authoring guide links intact).
  Keep the existing vignette checklist and template links working.
- [ ] **Step 2: Build + verify internal links** — `./.venv/bin/mkdocs build --strict` (strict fails on broken internal links). Expected: exit 0. Then `grep -q "Contribute a vignette" site/contribute/index.html && echo OK`.
- [ ] **Step 3: Commit** — `git add docs/contribute.md && git commit -m "Rework Contribute into per-pillar paths"`.

### Task 6.3: Whole-site QA gate

- [ ] **Step 1: Clean strict build** — `rm -rf site && ./.venv/bin/mkdocs build --strict`. Expected: exit 0, no warnings.
- [ ] **Step 2: Structural assertions** —
  ```bash
  for p in index data/index library/index vignettes/index contribute about data/schemas/gks-bundle; do
    test -f "site/$p/index.html" 2>/dev/null || test -f "site/$p.html" || { echo "MISSING: $p"; }
  done
  echo "structure check done"
  ```
  Resolve any `MISSING` before proceeding. (Note: `site/index.html` is at root, not `site/index/`.)
- [ ] **Step 3: Nav order check** — `mkdocs serve` and confirm the top nav reads **Home · Data Bundles · Python Package · Vignettes · Contribute · About** (pipeline order), tabs switch on the landing, and the audience cards + pipeline strip render. Optionally headless-screenshot the landing and the schema page.
- [ ] **Step 4: Link sanity** — confirm the three audience-routing links and the landing → Data Bundles schema link all resolve (strict build already guarantees internal links; this is a click-through confirmation).
- [ ] **Step 5: Merge** — per @superpowers:finishing-a-development-branch, merge `v2-approach-c` to `main` (or open a PR). The existing publish workflow deploys on push to `main`.

---

## Acceptance criteria (v2 Approach C)

The reorganization is complete when:

1. `mkdocs build --strict` passes on a clean tree with the three-pillar nav in pipeline order.
2. The landing page renders the value narrative, the pipeline visual, the three audience-routing cards, and the working four-altitude content-tabs demo.
3. **Data Bundles** has an overview page and a **browsable, auto-generated** schema page produced from a committed self-contained schema via `json-schema-for-humans` + gen-files.
4. **Python Package** has an overview page describing load → explore → export and explicitly marking the package build and `CustomProposition` as forthcoming (with links).
5. **Vignettes** is repositioned as Pillar 3 with the v1 catalog machinery, template, patterns vocabulary, and BRCA Exchange vignette **intact and still rendering**.
6. **About** reflects the three-pillar model; **Contribute** offers three per-pillar paths with the vignette path fully preserved.
7. `pymdownx.inlinehilite` and `pymdownx.tabbed` are enabled and demonstrably rendering.

## Deferred to their own spec → plan cycles (explicitly NOT in this plan)

- The Pillar 2 **Python package** implementation (loaders, in-memory model, exporters).
- The **`CustomProposition`** object in va-spec / va-spec-python (schema + Pydantic model + validation).
- **Live-service registration** for very large datasets, and **remote-`$ref` schema rendering** of the full GKS bundle schema.
- Additional partner bundles (ClinVar GKS, CIViC) beyond the demonstrator schema.
- Additional vignettes beyond the preserved BRCA Exchange worked example.
- Landing-page visual polish requiring the `frontend-design` plugin (currently not enabled).
