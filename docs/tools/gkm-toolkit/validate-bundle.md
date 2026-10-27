---
title: Validate a bundle file
---

# Validate a bundle file

[`load_bundle`](api/loading.md) reads a whole bundle into memory before it
validates it. Published bundles can be several gigabytes, so the GKM Toolkit also
offers **streaming validation**. It reads the bundle file once, in pieces, and
checks every record exactly as published. It can also write a stamped
verification report that records what was checked, against which schemas, and
the result.

This is useful when you produce GKM bundles and need an auditable record that a
specific published file validates.

## Install

Streaming validation needs [`ijson`](https://pypi.org/project/ijson/), which is
included in the `streaming` extra:

```shell
python3 -m pip install "ga4gh.gkm[streaming]" --pre
```

## Validate from the command line

The `gkm-validate-bundle` command validates a `.json` bundle or a
gzip-compressed one (`.json.gz`):

```shell
gkm-validate-bundle my-bundle.json.gz \
  --schema schema/my-bundle.schema.json \
  --schema-dir schema \
  --url https://example.org/releases/my-bundle.json.gz \
  --report my-bundle.validation.json
```

| Option | Purpose |
| --- | --- |
| `--schema PATH` | The producer bundle JSON Schema (Draft 2020-12). |
| `--schema-id URI` | The bundle schema's `$id`, looked up in `--schema-dir`. Use it instead of `--schema`, or with it to confirm the file's `$id`. |
| `--schema-dir DIR` | A directory of JSON Schemas that the bundle schema references, searched recursively. You can repeat it. Schemas from the installed [reference implementations](../reference-implementations.md) are always available. A local schema replaces an installed one with the same `$id`. |
| `--workers N` | The number of validating processes. The default is the CPU count minus one. |
| `--chunk-size N` | The number of records validated together. The default is 2000. |
| `--sidecar PATH` | A file holding the bundle's published SHA-256 digest. The default is `<bundle>.sha256` if it exists. |
| `--url URL` | Where the bundle is published. This is recorded in the report. |
| `--report PATH` | Write the JSON report to `PATH`, with a Markdown summary beside it (same name, `.md`). |
| `--sections a,b` | Validate only these sections, for debugging. The report then fails. |
| `--allow-empty-sections` | Do not fail the report when a section has no records. |
| `--quiet` | Print only the result line. |

The command exits with `0` when every check passes, `1` when a check fails, and
`2` when validation cannot run, for example when the schema cannot be found.

## Validate from Python

```python
from ga4gh.gkm.bundles import validate_bundle_stream

result = validate_bundle_stream(
    "my-bundle.json.gz",
    "schema/my-bundle.schema.json",
    schema_dirs=["schema"],
    workers=4,
    url="https://example.org/releases/my-bundle.json.gz",
)
print(result.passed, result.records, result.failing)
result.write_report("my-bundle.validation.json")
```

## What is checked

Each top-level object other than `metadata` is a **section**. Each entry in a
section is a **record**. The bundle passes when:

- every top-level value with a `const` in the schema matches it, for example a
  `schema_version`;
- every top-level property the schema requires is present;
- the SHA-256 digest of the bytes read matches the sidecar, when there is one;
- every section has at least one record, unless `--allow-empty-sections` is set;
- every record, every other top-level value, and every empty section validates
  against the bundle schema; and
- no section was skipped with `--sections`.

Records are checked as published, with
[`validate_bundle_schema`](api/schema-validation.md). Each chunk of records from
one section is wrapped as a one-section bundle and validated against the bundle
schema. If a chunk fails, each of its records is checked alone to find the ones
that fail.

!!! note "Streaming validation does not follow bundle-local links"

    The targets of bundle-local JSON Pointers (`#/...`) can be anywhere in the
    file, so streaming validation does not resolve or expand them. Records are
    checked with their links as written. The report warns when records contain
    such links. Constraints over a whole section, such as `maxProperties`, are
    checked for each chunk only.

## The verification report

The JSON report contains:

| Field | Contents |
| --- | --- |
| `result` | `PASS` or `FAIL`. |
| `started_at`, `finished_at`, `duration_seconds` | When the run started and finished (UTC), and how long it took. |
| `bundle` | The file name, published URL, compression, size, the SHA-256 of the bytes read, the sidecar and its digest, and the top-level scalar values. |
| `validator` | The function and mode used, the versions of `ga4gh.gkm`, the reference implementations, `jsonschema`, `referencing`, `ijson` and Python, and the worker and chunk settings. |
| `schemas` | The bundle schema's `$id`, file and SHA-256, the schema directories, and how many schema files were loaded. |
| `totals` | The number of sections, records and failures. |
| `sections` | For each section: its records, failing records, record `type` counts, and the schemas its records are validated against. |
| `checks` | Each check, with what was expected, what was found, and its result. |
| `warnings` | Anything that limits the result, such as a missing sidecar. |
| `failures_sample` | Up to 50 failing records, each with its error. |

For each section, `schemas` lists the schemas that the bundle schema names for
its records. These are the `$ref` targets of the record schema, reached directly
or through `oneOf`, `anyOf` or `allOf`. Schemas they reference in turn are not
listed. Each entry gives:

- the schema's `$id`, `title`, standard and version;
- the combining keyword (`oneOf`, `anyOf` or `allOf`), if there is one;
- the key pattern the section uses for this schema;
- `source`: `file` for a schema from `--schema-dir`, with its `file` and
  `file_sha256`, or `installed model` for one from an installed reference
  implementation; and
- `records`: how many records have this schema's `type`. When the type does not
  identify a single schema, this is `null`.

File paths appear in the report as you gave them. Use relative paths for
`--schema` and `--schema-dir` if you will publish the report.

The Markdown summary shows the same results as tables: the bundle, the sections,
the schemas applied to each section, the checks, the warnings, and the first
failures.
