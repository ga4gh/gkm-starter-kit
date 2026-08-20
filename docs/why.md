# Why GKM and the Starter Kit matter

Standards matter when they make collaboration easier. The benefits show up
differently for data producers, data consumers, and the GKM community.

## Ways to use GKM

Using a GKM standard does not imply reading or writing bundles. Producers and
consumers can use the standards through several interfaces:

- **Python reference implementations** construct, validate, and serialize
  individual GKM objects. See [What is GKM?](about.md#what-is-gkm) for the
  libraries available for each standard.
- **Resource APIs** can expose GKM objects for consumers to query in place. This
  is often a better fit for large or frequently updated resources.
- **Bundles** package related GKM objects in producer-defined JSON documents.
  The Starter Kit Python package supports this file-based workflow.

These approaches can be used independently or together. Bundles are not a
requirement of GKM, and the Starter Kit does not replace the reference
implementations or resource APIs.

## Value for producers

Shared GKM models let producers publish knowledge for a wider audience without
inventing new semantics for every consumer. When a producer uses bundles, a
documented, versioned bundle format also makes structural changes easier to
communicate and adopt.

## Value for consumers

Consumers spend less time translating unfamiliar data and more time using it.
They can bring additional resources into an existing workflow, compare
knowledge across sources, and trace relationships back to the original data.

## Value for the GKM community

Real data and working implementations test the standards in ways that examples
alone cannot. They reveal gaps, establish reusable patterns, and show where GKM
is already delivering practical results.

As more producers participate, the amount of interoperable genomic knowledge
grows. Each new resource becomes easier for existing consumers to adopt, and
each proven use case makes the next implementation easier to justify.

Next, explore [Data Bundles](data/index.md) or start with the [Python
Package](library/index.md).
