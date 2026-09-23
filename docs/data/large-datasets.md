# Large-volume datasets

<span class="gks-status gks-status--pilot">In development</span>

[Native records](native-records.md) and [compact bundles](bundles/index.md)
both distribute GKM knowledge as JSON documents. That works well until the
volume grows to the point where a single document is impractical to produce,
transfer, or load into memory. Some producers need to share GKM records by the
hundreds of thousands or millions.

For that scale, work is underway on **bulk-friendly formats** that let consumers
query large collections without reading everything at once.

!!! warning "Not yet available"

    This method is a work in progress. The formats and tooling described below
    are being designed and prioritized with community partners, and are not
    ready to use yet. This page will be updated as support takes shape.

## Parquet export

The primary direction is a **[Apache Parquet](https://parquet.apache.org/)**
export of GKM records drawn from a common set of classes. Parquet is a
columnar, compressed format that is well suited to large, uniform collections
and is widely supported by data-analysis tools.

The goal is to let a consumer read a producer's GKM records — variants,
propositions, evidence, assertions, and the objects they depend on — directly
into analytics environments and query them at scale.

## Relational format

A **relational database dump** is also being considered, distributing the same
records as normalized tables that can be loaded into a relational database. This
would let consumers join and filter GKM records using standard SQL alongside
their existing data.

## Status and feedback

Both directions are early and may change. If your resource needs to share GKM
records at this scale, or you have requirements for a particular format, that
input helps prioritize the work — see the
[Tools pillar](../tools/index.md) for how these formats will be validated and
accessed as they become available.
