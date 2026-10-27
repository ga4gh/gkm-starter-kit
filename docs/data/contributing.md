# Contribute to Data

A [bundle example](bundle/examples.md) is a small, focused subset of a
producer's actual published dataset containing genuine, unmodified GKM records.
It shows how a producer groups records, links shared objects, and records
provenance without requiring readers to download the complete dataset.

## Contribute a bundle example

Before preparing a new bundle example,
[open an issue](https://github.com/ga4gh/gkm-starter-kit/issues/new) and agree on
the scope with maintainers. This lets maintainers confirm that the example fits
the project's use cases before you invest time in preparing it.

In the proposal, explain what the bundle example will teach, which GKM standards
and versions it will use, and which producer and published dataset it comes
from. Identify the source records or dataset release and the reuse terms. You
do not need to prepare the bundle files before discussing the scope.

You can propose a new bundle example, improve an existing one, or clarify the
[bundle guidance](bundle/schemas-and-contents.md). The
[bundle examples](bundle/examples.md) show the current format. Small
documentation corrections can go directly into a PR.

!!! note "Complete datasets"
    Maintainers are still developing the hosting and review process for adding
    new complete datasets to the [public bundle repository](bundle/repository.md).
    Adding a complete dataset is not yet a self-service contribution path.

## Prepare a bundle example

Once the scope is agreed, include the bundle schema alongside the JSON bundle
so readers can see which collections, metadata, and object types are expected.
The [bundle schemas and contents guide](bundle/schemas-and-contents.md)
explains versioned schema references, local JSON Pointers, and
producer-specific fields.

Use genuine, unmodified records from the producer's published dataset, and
record their source and provenance. Include only data you have permission to
share publicly. Do not include private patient information or other restricted
content. Check that local references resolve and that the bundle matches
its schema before asking others to use it.

## Check and propose the change

Follow the [development guide](../tools/gkm-toolkit/development.md) to set up the
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
