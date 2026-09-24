# Large-volume datasets

Both [native records](native-records.md) and
[bundles (compact records)](bundles/index.md) distribute GKM knowledge as JSON
documents. This works well until the volume grows to the point where a single
document is impractical to produce, transfer, or load into memory. Some
producers need to share GKM records by the hundreds of thousands or millions.

Planned **bulk-friendly formats** will let consumers query large collections
without reading everything at once.

!!! warning "Not yet available"

    The formats and tooling below are in development. Community partners are
    helping prioritize the work.

## Parquet export

The primary direction is a **[Apache Parquet](https://parquet.apache.org/)**
export of GKM records drawn from a common set of classes. Parquet is a
columnar, compressed format that is well suited to large, uniform collections
and is widely supported by data-analysis tools.

The goal is to let consumers read a producer's GKM records, including variants,
propositions, evidence, assertions, and their dependencies, directly into
analytics environments and query them at scale.

## Relational format

A **relational database dump** is also being considered, distributing the same
records as normalized tables that can be loaded into a relational database. This
would let consumers join and filter GKM records using standard SQL alongside
their existing data.

## Status and feedback

If your resource needs to share GKM records at this scale or has requirements
for a particular format, share them to help prioritize the work. See the
[Tools pillar](../tools/index.md) for how these formats will be validated and
accessed as they become available.
