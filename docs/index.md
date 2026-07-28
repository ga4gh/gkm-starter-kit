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
