import gzip
import json

from ga4gh.gkm.cli import EXIT_ERROR, EXIT_FAIL, EXIT_PASS, validate_bundle_main

SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "items": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "required": ["name"],
                "properties": {"name": {"type": "string"}},
            },
        }
    },
}


def write_inputs(tmp_path, items):
    schema = tmp_path / "bundle.schema.json"
    schema.write_text(json.dumps(SCHEMA))
    bundle = tmp_path / "bundle.json.gz"
    bundle.write_bytes(gzip.compress(json.dumps({"items": items}).encode()))
    return bundle, schema


def test_cli_passes_and_writes_report(tmp_path, capsys):
    bundle, schema = write_inputs(tmp_path, {"a.1": {"name": "one"}})
    report = tmp_path / "report.json"

    status = validate_bundle_main(
        [
            str(bundle),
            "--schema",
            str(schema),
            "--workers",
            "1",
            "--url",
            "https://example.org/bundle.json.gz",
            "--report",
            str(report),
        ]
    )

    assert status == EXIT_PASS
    output = capsys.readouterr().out
    assert output.rstrip().endswith("PASS: 1 records, 0 failing")
    assert "items" in output
    assert json.loads(report.read_text())["bundle"]["url"] == (
        "https://example.org/bundle.json.gz"
    )
    assert (tmp_path / "report.md").is_file()


def test_cli_fails_invalid_record(tmp_path, capsys):
    bundle, schema = write_inputs(tmp_path, {"a.1": {"name": 1}})

    status = validate_bundle_main(
        [str(bundle), "--schema", str(schema), "--workers", "1", "--quiet"]
    )

    assert status == EXIT_FAIL
    assert capsys.readouterr().out == "FAIL: 1 records, 1 failing\n"


def test_cli_reports_setup_errors(tmp_path, capsys):
    bundle, _ = write_inputs(tmp_path, {"a.1": {"name": "one"}})

    status = validate_bundle_main([str(bundle), "--workers", "1"])

    assert status == EXIT_ERROR
    assert "JSON Schema is required" in capsys.readouterr().err
