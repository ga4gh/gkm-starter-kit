# API reference

The API reference documents the public classes, functions, and exceptions in
`ga4gh.gkm.bundles`.

- [Containers](containers.md) — inspect collections, resolve references, and
  serialize bundles.
- [Loading](loading.md) — load one or several bundles from files,
  streams, registered names, or the public bundle repository.
- [Pointers](pointers.md) — validate bundle-local JSON Pointers.
- [Schema resolution](schema-resolution.md) — find the schema node and external
  reference for a bundle-local pointer target.
- [Model conversion](model-conversion.md) — convert bundle values to installed
  GA4GH models.
- [Compatibility](compatibility.md) — view supported GKM product versions and
  check a producer's bundle schema.
- [Registry](registry.md) — associate names with bundle and schema
  sources.
- [Bundle repository](repository.md) — retrieve bundles and schemas from the
  canonical public R2 repository.
- [Errors](errors.md) — package-specific exception hierarchy.
