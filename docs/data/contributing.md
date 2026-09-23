# Contribute to Data

A small GKM bundle can show how a producer groups records, links shared
objects, and records provenance. You can propose an example without publishing
a complete dataset.

## Choose a contribution

- **A focused example or documentation fix:** Propose a small, publicly
  shareable bundle and its schema, improve an existing example, or clarify the
  [bundle guidance](bundles/schemas-and-contents.md). The
  [mini bundle examples](bundles/mini-examples.md) show the current format.
- **A complete public dataset:** The [public bundle repository](bundles/repository.md)
  provides complete, published GKM bundles and their schemas. Adding another
  dataset is not yet a self-service process; hosting and review guidance is
  still being developed.
  [Open an issue](https://github.com/ga4gh/gkm-starter-kit/issues/new) to
  discuss the resource with maintainers before preparing a dataset PR.

## Prepare a focused example

For an issue proposal, explain what the example will teach and which GKM
standards and versions you plan to use. For source-derived data, identify the
producer, source record or dataset release, and reuse terms. For a synthetic
example, say that it is synthetic and describe what it illustrates. You do not
need to prepare the bundle files before discussing the scope.

Once the scope is agreed, include the bundle schema alongside the JSON bundle
so readers can see which collections, metadata, and object types are expected.
The [bundle schemas and contents guide](bundles/schemas-and-contents.md)
explains versioned schema references, local JSON Pointers, and
producer-specific fields. Record the source and provenance when the example
derives from real data.
Include only data you have permission to share publicly. Do not include private
patient information or other restricted content. If the example is synthetic
or adapted, label it as such and explain how it was created or adapted. Check
that local references resolve and that the bundle matches its schema before
asking others to use it.

## Propose and check the change

For a new example, [open an issue](https://github.com/ga4gh/gkm-starter-kit/issues/new)
with the proposed scope and information above. A small correction to an
existing page can go directly into a PR. Once the scope is clear, follow the
[development guide](../tools/gkm-toolkit/development.md) to set up the
repository and run the relevant checks. For a documentation change, the guide's
strict build is:

```shell
python -m scripts.build_docs
zensical build --clean --strict
```

The Toolkit API documents [schema validation](../tools/gkm-toolkit/api/schema-validation.md)
and [bundle-local pointer checks](../tools/gkm-toolkit/api/pointers.md). The
documentation build checks the generated site and internal links; it does not
establish that a proposed bundle is valid or licensed for reuse. Explain the
checks you ran in the PR.
