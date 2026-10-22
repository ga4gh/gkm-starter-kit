import gzip
import hashlib
import json
from pathlib import Path

import pytest

from ga4gh.gkm import bundles
from ga4gh.gkm.bundles import (
    BundleNotFoundError,
    BundleSerializationError,
    load_schema_directory,
    supported_gkm_versions,
    validate_bundle_stream,
)
from ga4gh.gkm.bundles.streaming import build_schema_registry

DRAFT_202012 = "https://json-schema.org/draft/2020-12/schema"
BASE = "https://example.org/schema/example/1.0.0/json"
RECORD_ID = f"{BASE}/Record"
NOTE_ID = f"{BASE}/Note"
BUNDLE_ID = f"{BASE}/ExampleBundle"


def record_schema(name: str) -> dict:
    field = "name" if name == "Record" else "text"
    return {
        "$schema": DRAFT_202012,
        "$id": f"{BASE}/{name}",
        "title": name,
        "type": "object",
        "properties": {"type": {"const": name}, field: {"type": "string"}},
        "required": ["type", field],
    }


def bundle_schema(*, min_items: int = 1) -> dict:
    return {
        "$schema": DRAFT_202012,
        "$id": BUNDLE_ID,
        "type": "object",
        "properties": {
            "schema_version": {"type": "string", "const": "1.0.0"},
            "metadata": {"type": "object"},
            "records": {
                "type": "object",
                "minProperties": 1,
                "patternProperties": {"^rec:": {"$ref": RECORD_ID}},
                "additionalProperties": False,
            },
            "items": {
                "type": "object",
                "minProperties": min_items,
                "additionalProperties": {
                    "anyOf": [{"$ref": RECORD_ID}, {"$ref": NOTE_ID}]
                },
            },
        },
        "required": ["schema_version", "records"],
        "additionalProperties": False,
    }


def valid_bundle() -> dict:
    # Keys contain dots: depth must not be derived from the ijson prefix.
    return {
        "schema_version": "1.0.0",
        "metadata": {"producer": "example", "tags": ["a", "b"]},
        "records": {
            f"rec:ga4gh.SL.{index}": {"type": "Record", "name": f"record {index}"}
            for index in range(5)
        },
        "items": {
            "clinvar.trait:1": {"type": "Record", "name": "one"},
            "clinvar.submission:SCV1.2": {"type": "Note", "text": "two"},
            "note.3": {"type": "Note", "text": "three"},
        },
    }


@pytest.fixture
def schema_dir(tmp_path) -> Path:
    directory = tmp_path / "schemas" / "example" / "json"
    directory.mkdir(parents=True)
    for name in ("Record", "Note"):
        (directory / name).write_text(json.dumps(record_schema(name)))
    (directory / "README.md").write_text("not a schema")
    (directory / "unrelated.json").write_text(json.dumps({"no": "id"}))
    return tmp_path / "schemas"


@pytest.fixture
def schema_path(tmp_path) -> Path:
    path = tmp_path / "bundle.schema.json"
    path.write_text(json.dumps(bundle_schema()))
    return path


def write_bundle(path: Path, document: dict, *, sidecar: bool = True) -> Path:
    data = json.dumps(document).encode()
    raw = gzip.compress(data) if path.suffix == ".gz" else data
    path.write_bytes(raw)
    if sidecar:
        digest = hashlib.sha256(raw).hexdigest()
        path.with_name(path.name + ".sha256").write_text(f"{digest}  {path.name}\n")
    return path


def check(result, prefix: str) -> dict:
    return next(
        item for item in result.report["checks"] if item["check"].startswith(prefix)
    )


def test_validates_every_record_with_dotted_keys(tmp_path, schema_path, schema_dir):
    bundle = write_bundle(tmp_path / "example.json.gz", valid_bundle())

    result = validate_bundle_stream(
        bundle, schema_path, schema_dirs=[schema_dir], chunk_size=2
    )

    assert result.passed, result.report
    assert result.records == 8
    assert result.failing == 0
    sections = {section["name"]: section for section in result.report["sections"]}
    assert list(sections) == ["records", "items"]
    assert sections["records"]["records"] == 5
    assert sections["items"]["records"] == 3
    assert sections["items"]["record_types"] == {"Note": 2, "Record": 1}
    assert result.report["bundle"]["top_level_values"] == {"schema_version": "1.0.0"}
    assert result.report["bundle"]["compression"] == "gzip"
    assert check(result, "sha256")["result"] == "PASS"
    assert result.report["warnings"] == []


def test_validates_uncompressed_bundle_in_worker_processes(
    tmp_path, schema_path, schema_dir
):
    bundle = write_bundle(tmp_path / "example.json", valid_bundle(), sidecar=False)

    result = validate_bundle_stream(
        bundle, schema_path, schema_dirs=[schema_dir], workers=2, chunk_size=1
    )

    assert result.passed
    assert result.records == 8
    assert result.report["bundle"]["compression"] is None
    assert check(result, "sha256")["result"] == "NOT CHECKED (no sidecar)"
    assert any("sidecar" in warning for warning in result.report["warnings"])


def test_reports_failing_record(tmp_path, schema_path, schema_dir):
    document = valid_bundle()
    document["records"]["rec:bad.1"] = {"type": "Record"}
    bundle = write_bundle(tmp_path / "example.json.gz", document)

    result = validate_bundle_stream(
        bundle, schema_path, schema_dirs=[schema_dir], chunk_size=4
    )

    assert not result.passed
    assert result.failing == 1
    assert check(result, "every record validates")["result"] == "FAIL"
    [failure] = result.report["failures_sample"]
    assert failure.startswith("records/rec:bad.1: ")
    assert "'name' is a required property" in failure
    sections = {section["name"]: section for section in result.report["sections"]}
    assert sections["records"]["failing"] == 1


def test_fails_empty_section(tmp_path, schema_path, schema_dir):
    document = valid_bundle()
    document["items"] = {}
    bundle = write_bundle(tmp_path / "example.json.gz", document)

    result = validate_bundle_stream(bundle, schema_path, schema_dirs=[schema_dir])

    assert not result.passed
    assert check(result, "every section has")["empty_sections"] == ["items"]
    assert check(result, "every section has")["result"] == "FAIL"
    # The empty section is still validated against the schema (minProperties).
    assert check(result, "top-level values")["result"] == "FAIL"


def test_allows_empty_section_the_schema_permits(tmp_path, schema_dir):
    schema_path = tmp_path / "bundle.schema.json"
    schema_path.write_text(json.dumps(bundle_schema(min_items=0)))
    document = valid_bundle()
    document["items"] = {}
    bundle = write_bundle(tmp_path / "example.json.gz", document)

    result = validate_bundle_stream(
        bundle, schema_path, schema_dirs=[schema_dir], allow_empty_sections=True
    )

    assert result.passed
    assert check(result, "every section has")["result"] == "ALLOWED"


def test_fails_sidecar_mismatch(tmp_path, schema_path, schema_dir):
    bundle = write_bundle(tmp_path / "example.json.gz", valid_bundle())
    other = tmp_path / "published.sha256"
    other.write_text("0" * 64 + "  example.json.gz\n")

    result = validate_bundle_stream(
        bundle, schema_path, schema_dirs=[schema_dir], sidecar=other
    )

    assert not result.passed
    sha_check = check(result, "sha256")
    assert sha_check["result"] == "FAIL"
    assert sha_check["expected"] == "0" * 64
    assert sha_check["found"] == hashlib.sha256(bundle.read_bytes()).hexdigest()


def test_fails_schema_const_and_required_checks(tmp_path, schema_path, schema_dir):
    document = valid_bundle()
    document["schema_version"] = "0.9.0"
    del document["records"]
    bundle = write_bundle(tmp_path / "example.json.gz", document)

    result = validate_bundle_stream(bundle, schema_path, schema_dirs=[schema_dir])

    assert not result.passed
    const_check = check(result, "bundle schema_version")
    assert const_check["result"] == "FAIL"
    assert const_check["expected"] == "1.0.0"
    assert const_check["found"] == "0.9.0"
    assert check(result, "every top-level property")["missing"] == ["records"]


def test_writes_report_json_and_markdown(tmp_path, schema_path, schema_dir):
    bundle = write_bundle(tmp_path / "example.json.gz", valid_bundle())
    url = "https://example.org/data/example.json.gz"
    result = validate_bundle_stream(
        bundle, schema_path, schema_dirs=[schema_dir], url=url
    )

    json_path, markdown_path = result.write_report(tmp_path / "out.validation.json")

    report = json.loads(json_path.read_text())
    assert report["report"] == "GKM bundle validation report"
    assert report["report_version"] == 1
    assert report["result"] == "PASS"
    for key in ("started_at", "finished_at"):
        assert report[key].endswith("Z")
    assert isinstance(report["duration_seconds"], int)
    assert report["bundle"] == {
        "file": "example.json.gz",
        "url": url,
        "compression": "gzip",
        "size_bytes": bundle.stat().st_size,
        "sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
        "sidecar": str(bundle) + ".sha256",
        "published_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
        "top_level_values": {"schema_version": "1.0.0"},
    }
    versions = report["validator"]["versions"]
    assert {"ga4gh.gkm", "jsonschema", "referencing", "ijson", "python"} <= set(
        versions
    )
    assert report["schemas"]["bundle_schema_id"] == BUNDLE_ID
    assert report["schemas"]["bundle_schema_file"] == str(schema_path)
    assert (
        report["schemas"]["bundle_schema_sha256"]
        == hashlib.sha256(schema_path.read_bytes()).hexdigest()
    )
    assert report["schemas"]["schema_files_loaded"] == 2
    assert report["totals"] == {"sections": 2, "records": 8, "failing": 0}

    sections = {section["name"]: section for section in report["sections"]}
    [record_schema_entry] = sections["records"]["schemas"]
    record_file = schema_dir / "example" / "json" / "Record"
    assert record_schema_entry == {
        "key_pattern": "^rec:",
        "combined_by": None,
        "$id": RECORD_ID,
        "title": "Record",
        "standard": "example",
        "version": "1.0.0",
        "record_type": "Record",
        "source": "file",
        "file": str(record_file),
        "file_sha256": hashlib.sha256(record_file.read_bytes()).hexdigest(),
        "resolved": True,
        "records": 5,
    }
    items = sections["items"]["schemas"]
    assert [entry["$id"] for entry in items] == [RECORD_ID, NOTE_ID]
    assert {entry["combined_by"] for entry in items} == {"anyOf"}
    assert [entry["records"] for entry in items] == [1, 2]
    assert {entry["key_pattern"] for entry in items} == {None}
    assert [item["result"] for item in report["checks"]] == ["PASS"] * 7
    assert report["warnings"] == []
    assert report["failures_sample"] == []

    markdown = markdown_path.read_text()
    assert markdown_path.name == "out.validation.md"
    assert markdown.startswith("# Validation report: `example.json.gz`")
    assert "**Result: PASS** · 8 records in 2 sections · 0 failing" in markdown
    assert f"| `items` | [Note]({NOTE_ID}) | example | 1.0.0 | anyOf | 2 |" in markdown
    assert "- PASS: every record validates against the bundle schema" in markdown


def test_finds_schema_by_id(tmp_path, schema_dir):
    (schema_dir / "bundle.json").write_text(json.dumps(bundle_schema()))
    bundle = write_bundle(tmp_path / "example.json.gz", valid_bundle())

    result = validate_bundle_stream(
        bundle, schema_id=BUNDLE_ID, schema_dirs=[schema_dir]
    )

    assert result.passed
    assert result.report["schemas"]["bundle_schema_file"] == str(
        schema_dir / "bundle.json"
    )


def test_rejects_mismatched_schema_id(tmp_path, schema_path, schema_dir):
    bundle = write_bundle(tmp_path / "example.json.gz", valid_bundle())

    with pytest.raises(BundleSerializationError, match="does not match"):
        validate_bundle_stream(
            bundle,
            schema_path,
            schema_id="https://example.org/other",
            schema_dirs=[schema_dir],
        )
    with pytest.raises(BundleNotFoundError, match="No schema directory"):
        validate_bundle_stream(
            bundle, schema_id="https://example.org/other", schema_dirs=[schema_dir]
        )


def test_requires_a_schema(tmp_path):
    bundle = write_bundle(tmp_path / "example.json.gz", valid_bundle())

    with pytest.raises(BundleSerializationError, match="JSON Schema is required"):
        validate_bundle_stream(bundle)


def test_uses_registered_bundle_and_schema(tmp_path, schema_path, schema_dir):
    bundle = write_bundle(tmp_path / "example.json.gz", valid_bundle())
    bundles.registry.register(
        bundles.BundleRegistration(
            name="streaming-example", source=bundle, schema=schema_path
        ),
        replace=True,
    )

    result = validate_bundle_stream("streaming-example", schema_dirs=[schema_dir])

    assert result.passed


def test_unresolved_reference_fails_records_and_warns(tmp_path, schema_path):
    bundle = write_bundle(tmp_path / "example.json.gz", valid_bundle())

    result = validate_bundle_stream(bundle, schema_path)

    assert not result.passed
    assert result.failing == 8
    assert "could not be resolved locally" in result.report["failures_sample"][0]
    assert any(
        "schemas not available locally" in warning
        for warning in result.report["warnings"]
    )


def test_resolves_installed_model_schemas(tmp_path, sequence_id):
    vrs = supported_gkm_versions()["vrs"]
    reference = f"https://w3id.org/ga4gh/schema/vrs/{vrs}/json/SequenceReference"
    schema = {
        "$schema": DRAFT_202012,
        "type": "object",
        "properties": {
            "sequence": {"type": "object", "additionalProperties": {"$ref": reference}}
        },
    }
    document = {
        "sequence": {
            sequence_id: {"type": "SequenceReference", "refgetAccession": sequence_id},
        }
    }
    bundle = write_bundle(tmp_path / "vrs.json", document, sidecar=False)

    result = validate_bundle_stream(bundle, schema)

    assert result.passed, result.report["failures_sample"]
    [entry] = result.report["sections"][0]["schemas"]
    assert entry["source"] == "installed model"
    assert entry["standard"] == "vrs"
    assert entry["version"] == vrs
    assert entry["file"] is None
    assert result.report["schemas"]["bundle_schema_file"] is None


def test_warns_about_bundle_local_pointers(tmp_path):
    schema = {
        "$schema": DRAFT_202012,
        "type": "object",
        "properties": {"items": {"type": "object"}},
    }
    document = {"items": {"a": {"link": "#/items/b"}, "b": {"value": 1}}}
    bundle = write_bundle(tmp_path / "pointers.json", document, sidecar=False)

    result = validate_bundle_stream(bundle, schema)

    assert result.passed
    assert any(
        "1 records contain bundle-local JSON Pointers" in warning
        for warning in result.report["warnings"]
    )
    assert result.report["sections"][0]["schemas"] == []


def test_skipped_sections_fail(tmp_path, schema_path, schema_dir):
    bundle = write_bundle(tmp_path / "example.json.gz", valid_bundle())

    result = validate_bundle_stream(
        bundle, schema_path, schema_dirs=[schema_dir], sections=["records"]
    )

    assert not result.passed
    assert check(result, "every section validated")["skipped"] == {"items": 3}
    sections = {section["name"]: section for section in result.report["sections"]}
    assert sections["items"]["validated"] is False
    assert sections["items"]["records"] == 3


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        (b"[1, 2]", "must be a JSON object"),
        (b'{"items": {"a": ', "Invalid JSON"),
    ],
)
def test_rejects_invalid_documents(tmp_path, raw, message):
    bundle = tmp_path / "bad.json"
    bundle.write_bytes(raw)
    schema = {"$schema": DRAFT_202012, "type": "object"}

    with pytest.raises(BundleSerializationError, match=message):
        validate_bundle_stream(bundle, schema)


def test_rejects_invalid_arguments(tmp_path, schema_path):
    bundle = write_bundle(tmp_path / "example.json", valid_bundle())

    with pytest.raises(ValueError, match="must be positive"):
        validate_bundle_stream(bundle, schema_path, workers=0)
    with pytest.raises(BundleNotFoundError, match="Bundle source does not exist"):
        validate_bundle_stream(tmp_path / "missing.json", schema_path)
    with pytest.raises(BundleNotFoundError, match="Bundle schema does not exist"):
        validate_bundle_stream(bundle, tmp_path / "missing.schema.json")
    with pytest.raises(BundleNotFoundError, match="sidecar does not exist"):
        validate_bundle_stream(bundle, schema_path, sidecar=tmp_path / "missing")
    with pytest.raises(BundleSerializationError, match="Draft 2020-12"):
        validate_bundle_stream(bundle, {"type": "object"})


def test_load_schema_directory_rejects_conflicting_ids(tmp_path, schema_dir):
    conflict = schema_dir / "copy.json"
    conflict.write_text(json.dumps(record_schema("Record") | {"title": "Changed"}))

    with pytest.raises(BundleSerializationError, match="different contents"):
        load_schema_directory(schema_dir)
    with pytest.raises(BundleNotFoundError, match="does not exist"):
        load_schema_directory(tmp_path / "missing")


def test_build_schema_registry_prefers_local_files(schema_dir):
    vrs = supported_gkm_versions()["vrs"]
    reference = f"https://w3id.org/ga4gh/schema/vrs/{vrs}/json/SequenceReference"
    local = load_schema_directory(schema_dir)

    registry = build_schema_registry(local)

    assert registry.contents(RECORD_ID)["title"] == "Record"
    assert registry.contents(reference)["title"] == "SequenceReference"
