"""Command-line entry points for the GKM Toolkit."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import TYPE_CHECKING

from ga4gh.gkm.bundles.errors import BundleError
from ga4gh.gkm.bundles.streaming import validate_bundle_stream

if TYPE_CHECKING:
    from collections.abc import Sequence

EXIT_PASS = 0
"""Exit status when every check passed."""
EXIT_FAIL = 1
"""Exit status when the bundle failed a check."""
EXIT_ERROR = 2
"""Exit status when validation could not run, such as for a missing schema."""

_PRINTED_FAILURES = 20


def _validate_bundle_parser() -> argparse.ArgumentParser:
    """Build the ``gkm-validate-bundle`` argument parser.

    :return: The argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="gkm-validate-bundle",
        description=(
            "Stream a GKM bundle (.json or gzip-compressed) and validate every "
            "record against its producer JSON Schema, optionally writing a "
            "stamped verification report."
        ),
    )
    parser.add_argument("bundle", help="bundle file, .json or gzip-compressed")
    parser.add_argument(
        "--schema", help="producer bundle JSON Schema file (Draft 2020-12)"
    )
    parser.add_argument(
        "--schema-id",
        help="$id of the bundle schema, looked up in --schema-dir; checked "
        "against --schema when both are given",
    )
    parser.add_argument(
        "--schema-dir",
        action="append",
        default=[],
        metavar="DIR",
        help="directory of JSON Schemas (searched recursively) used to resolve "
        "the bundle schema's references, in addition to the schemas of the "
        "installed GA4GH reference implementations; may be repeated",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, (os.cpu_count() or 2) - 1),
        help="validating processes (default: CPU count minus one)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=2000,
        help="records per validated chunk (default: 2000)",
    )
    parser.add_argument(
        "--sidecar",
        help="file holding the bundle's published SHA-256 digest "
        "(default: <bundle>.sha256 when it exists)",
    )
    parser.add_argument("--url", help="published URL of the bundle, for the report")
    parser.add_argument(
        "--report",
        metavar="PATH",
        help="write the JSON verification report here and a Markdown summary "
        "beside it (same name, .md suffix)",
    )
    parser.add_argument(
        "--sections",
        help="comma-separated sections to validate; other sections are counted "
        "only, and the report fails",
    )
    parser.add_argument(
        "--allow-empty-sections",
        action="store_true",
        help="do not fail the report for sections without records",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="print only the result line"
    )
    return parser


def validate_bundle_main(argv: Sequence[str] | None = None) -> int:
    """Run ``gkm-validate-bundle``.

    :param argv: Command-line arguments, excluding the program name.
    :return: ``0`` when the bundle passed, ``1`` when it failed a check, and
        ``2`` when validation could not run.
    """
    args = _validate_bundle_parser().parse_args(argv)
    if not args.quiet:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        result = validate_bundle_stream(
            args.bundle,
            args.schema,
            schema_id=args.schema_id,
            schema_dirs=args.schema_dir,
            workers=args.workers,
            chunk_size=args.chunk_size,
            sidecar=args.sidecar,
            url=args.url,
            sections=args.sections.split(",") if args.sections else None,
            allow_empty_sections=args.allow_empty_sections,
        )
    except (BundleError, ImportError, ValueError) as error:
        sys.stderr.write(f"gkm-validate-bundle: error: {error}\n")
        return EXIT_ERROR

    report = result.to_dict()
    lines = []
    if not args.quiet:
        lines += [
            f"bundle: {report['bundle']['file']} ({report['bundle']['sha256']})",
            *(
                f"  {section['name']:32s} {section['records']:>12,d}  "
                f"failing {section['failing']:,d}"
                for section in report["sections"]
            ),
            *(f"  {check['result']}: {check['check']}" for check in report["checks"]),
            *(f"  WARNING: {warning}" for warning in report["warnings"]),
            *(
                f"  FAIL {failure}"
                for failure in report["failures_sample"][:_PRINTED_FAILURES]
            ),
        ]
    if args.report:
        json_path, markdown_path = result.write_report(args.report)
        lines.append(f"report: {json_path} (+ {markdown_path.name})")
    lines.append(
        f"{report['result']}: {result.records:,d} records, {result.failing:,d} failing"
    )
    sys.stdout.write("\n".join(lines) + "\n")
    return EXIT_PASS if result.passed else EXIT_FAIL


if __name__ == "__main__":  # pragma: no cover
    sys.exit(validate_bundle_main())
