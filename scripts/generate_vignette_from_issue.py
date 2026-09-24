"""Create a vignette draft from the body of a ``Propose a vignette`` issue.

The issue form is deliberately a proposal/triage mechanism, so it does not
collect everything needed for a published vignette.  This command carries its
structured fields into a valid vignette skeleton and leaves the remaining
editorial sections clearly marked for a maintainer to complete.

Usage:
    python -m scripts.generate_vignette_from_issue --issue 123
    python -m scripts.generate_vignette_from_issue --issue-file issue.md --dry-run

``--issue`` fetches an issue number or URL through the authenticated GitHub CLI
(``gh``). The generated file defaults to
``docs/user-stories/<source>/<slug>/vignette.md`` and will not overwrite an
existing file unless ``--force`` is supplied.

GitHub access is read-only: the command invokes only ``gh issue view`` and
never creates or changes issues, pull requests, comments, labels, or files on
GitHub.

When it writes a vignette locally, the command also adds or refreshes that
vignette's entry in ``zensical.toml`` so it remains visible in the sidebar.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import subprocess
import sys
from pathlib import Path

from scripts.vignette_loader import ALLOWED_PRODUCTS, REPO_ROOT, load_patterns, slugify

FIELD_LABELS = {
    "title": "Working title",
    "slug": "Slug",
    "source": "Source namespace",
    "summary": "Catalog summary",
    "implementer": "Implementer",
    "products": "GKM products and versions",
    "pattern": "Reuse pattern",
    "use_case": "Why this matters",
    "status": "Status",
    "tools": "Tools used",
    "links": "Relevant links",
    "additional_context": "Additional context",
}
IDENTIFIER_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LABELLED_URL_RE = re.compile(r"\[([^\]]+)]\s+(https?://[^\s<>()]+)")
BARE_URL_RE = re.compile(r"(?<!\]\()(?<!<)(https?://[^\s<>()]+)")
ZENSICAL_TOML = REPO_ROOT / "zensical.toml"
BROWSE_BY_IMPLEMENTER = '    { "Browse by implementer" = ['


def _parse_issue_body(body: str) -> dict[str, str]:
    """Extract fields from GitHub's rendered Markdown issue-form body."""
    values = {}
    headings = "|".join(re.escape(label) for label in FIELD_LABELS.values())
    for field, label in FIELD_LABELS.items():
        match = re.search(
            rf"^#{{2,3}} {re.escape(label)}\s*\n+(.*?)(?=^#{{2,3}} (?:{headings})\s*$|\Z)",
            body,
            flags=re.MULTILINE | re.DOTALL,
        )
        if match:
            values[field] = match.group(1).strip()
    return values


def _identifier(values: dict[str, str], field: str) -> str:
    """Return a required, kebab-case filesystem and YAML identifier."""
    value = _required(values, field)
    if not IDENTIFIER_RE.fullmatch(value):
        message = (
            f"{FIELD_LABELS[field]!r} must be a lowercase kebab-case identifier; "
            f"got {value!r}."
        )
        raise ValueError(message)
    return value


def _linkify(value: str) -> str:
    """Turn issue-form URLs into Markdown links without changing submitted labels."""
    labelled = LABELLED_URL_RE.sub(r"[\1](\2)", value)
    return BARE_URL_RE.sub(r"<\1>", labelled)


def _product_badges(products: list[tuple[str, str | None]]) -> str:
    """Render the product/version metadata as the documented product badges."""
    badges = []
    for name, version in products:
        product_class = name.lower()
        version_html = f" <small>{html.escape(version)}</small>" if version else ""
        badges.append(
            f'<span class="gks-product-label gks-product-label--{product_class}">'
            f"{html.escape(name)}{version_html}</span>"
        )
    return " ".join(badges)


def _status_badge(status: str) -> str:
    """Render a validated status as the documented status badge."""
    return f'<span class="gks-status gks-status--{status}">{status}</span>'


def _update_navigation(title: str, implementer: str, output: Path) -> None:
    """Add or refresh a vignette under its implementer's sidebar dropdown."""
    try:
        docs_path = output.resolve().relative_to((REPO_ROOT / "docs").resolve())
    except ValueError:
        return

    vignette_path = docs_path.as_posix()
    navigation = ZENSICAL_TOML.read_text(encoding="utf-8")
    implementer_path = f"user-stories/by-implementer/{slugify(implementer)}/index.md"
    legacy_group = re.compile(
        rf"^    \{{ {_yaml_string(implementer)} = \[\n"
        rf'      "{re.escape(implementer_path)}",\n'
        rf'        \{{ .* = "{re.escape(vignette_path)}" \}},\n'
        r"      \] \},\n",
        re.MULTILINE,
    )
    navigation = legacy_group.sub("", navigation)
    path_pattern = re.compile(
        rf'^\s*\{{ .* = "{re.escape(vignette_path)}" \}},?\n?', re.MULTILINE
    )
    navigation = path_pattern.sub("", navigation)
    browse_start = navigation.find(BROWSE_BY_IMPLEMENTER)
    if browse_start < 0:
        message = "Could not find the Browse by implementer navigation section."
        raise ValueError(message)
    browse_bracket_start = navigation.index("[", browse_start)
    depth = 0
    browse_bracket_end = -1
    for index, character in enumerate(
        navigation[browse_bracket_start:], browse_bracket_start
    ):
        if character == "[":
            depth += 1
        elif character == "]":
            depth -= 1
            if depth == 0:
                browse_bracket_end = index
                break
    if browse_bracket_end < 0:
        message = (
            "Could not find the end of the Browse by implementer navigation section."
        )
        raise ValueError(message)

    browse_navigation = navigation[browse_start:browse_bracket_end]
    group_start = re.search(
        rf"^\s*\{{ {_yaml_string(implementer)} = \[",
        browse_navigation,
        re.MULTILINE,
    )
    child_entry = f'        {{ {_yaml_string(title)} = "{vignette_path}" }},'
    if group_start:
        bracket_start = navigation.index("[", browse_start + group_start.start())
        depth = 0
        bracket_end = -1
        for index, character in enumerate(navigation[bracket_start:], bracket_start):
            if character == "[":
                depth += 1
            elif character == "]":
                depth -= 1
                if depth == 0:
                    bracket_end = index
                    break
        if bracket_end < 0:
            message = f"Could not find the end of {implementer!r} navigation group."
            raise ValueError(message)
        closing_line_start = navigation.rfind("\n", 0, bracket_end) + 1
        updated = (
            navigation[:closing_line_start]
            + f"{child_entry}\n"
            + navigation[closing_line_start:]
        )
    else:
        group = (
            f"      {{ {_yaml_string(implementer)} = [\n"
            f'        "{implementer_path}",\n'
            f"{child_entry}\n"
            "      ] },\n"
        )
        closing_line_start = navigation.rfind("\n", 0, browse_bracket_end) + 1
        preceding_navigation = navigation[:closing_line_start].rstrip()
        if not preceding_navigation.endswith(","):
            preceding_navigation += ","
        updated = f"{preceding_navigation}\n" + group + navigation[closing_line_start:]
    ZENSICAL_TOML.write_text(updated, encoding="utf-8")


def _required(values: dict[str, str], field: str) -> str:
    """Return a required issue field, with an actionable error if it is absent."""
    value = values.get(field, "")
    if not value or value == "_No response_":
        msg = f"Issue body is missing a response for {FIELD_LABELS[field]!r}."
        raise ValueError(msg)
    return value


def _products(value: str) -> list[tuple[str, str | None]]:
    """Parse one ``Product [version]`` entry per line from the issue form."""
    products = []
    for raw_line in value.splitlines():
        product_line = raw_line.strip().lstrip("- ").strip()
        if not product_line:
            continue
        name, _, version = product_line.partition(" ")
        if name not in ALLOWED_PRODUCTS:
            msg = f"Unknown GKM product {name!r}; expected one of {ALLOWED_PRODUCTS}."
            raise ValueError(msg)
        products.append((name, version.strip() or None))
    if not products:
        message = "At least one GKM product is required."
        raise ValueError(message)
    return products


def _issue_body(issue: str) -> str:
    """Fetch an issue body through the authenticated GitHub CLI."""
    # The fixed command uses no shell; ``issue`` is passed as one argument.
    result = subprocess.run(  # noqa: S603
        ["gh", "issue", "view", issue, "--json", "body", "--jq", ".body"],  # noqa: S607
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Unable to fetch issue with gh.")
    return result.stdout


def _yaml_string(value: str) -> str:
    """Return a safely double-quoted YAML scalar."""
    return json.dumps(value, ensure_ascii=False)


def _render(values: dict[str, str], new_pattern_slug: str | None) -> str:
    """Render a draft vignette from extracted form values."""
    title = _required(values, "title")
    slug = _identifier(values, "slug")
    _identifier(values, "source")
    summary = _required(values, "summary")
    implementer = _required(values, "implementer")
    use_case = _required(values, "use_case")
    status = _required(values, "status")
    if status not in ("production", "pilot", "proposal"):
        message = f"Invalid status {status!r}."
        raise ValueError(message)

    selected_pattern = _required(values, "pattern")
    patterns = load_patterns()
    if selected_pattern == "New pattern (describe below)":
        if not new_pattern_slug:
            message = (
                "A new pattern needs --new-pattern-slug and an entry in "
                "docs/user-stories/patterns.yml before the draft will validate."
            )
            raise ValueError(message)
        if not IDENTIFIER_RE.fullmatch(new_pattern_slug):
            message = f"New pattern slug must be lowercase kebab-case; got {new_pattern_slug!r}."
            raise ValueError(message)
        pattern = new_pattern_slug
    else:
        labels = {label: slug for slug, label in patterns.items()}
        try:
            pattern = labels[selected_pattern]
        except KeyError as exc:
            message = f"Unknown reuse pattern {selected_pattern!r}."
            raise ValueError(message) from exc

    products = _products(_required(values, "products"))
    product_badges = _product_badges(products)
    status_badge = _status_badge(status)
    product_lines = []
    for name, version in products:
        product_lines.append(f"  - name: {name}")
        if version:
            product_lines.append(f"    version: {_yaml_string(version)}")

    tools = _linkify(
        values.get("tools") or "TODO: Add concrete tools, versions, and links."
    )
    links = _linkify(
        values.get("links")
        or "TODO: Add relevant implementation, documentation, or publication links."
    )
    context = values.get("additional_context", "")
    story = "TODO: Expand the proposal into the real situation, the prior challenge, and what GKM unlocks."
    context_block = ""
    if context.startswith("The story\n"):
        story = context.removeprefix("The story").lstrip()
    elif context:
        context_block = f"\n## Proposal notes\n\n{context}\n"
    today = dt.datetime.now(tz=dt.UTC).date().isoformat()
    return f"""---
title: {_yaml_string(title)}
slug: {slug}
summary: {_yaml_string(summary)}
products:
{chr(10).join(product_lines)}
pattern: {pattern}
implementer: {_yaml_string(implementer)}
status: {status}
last_updated: {today}
---

# {title}

**Why this matters**

{use_case}

**At a glance**

- **Implementer:** {implementer}
- **Products:** {product_badges}
- **Pattern:** {selected_pattern}
- **Tools:** {tools}
- **Status:** {status_badge}

---

## The story

{story}

## The data

TODO: Add a lightly annotated real payload and any files under `payloads/`.

## The tools used

{tools}

## Relevant links

{links}

## How to reuse this pattern

TODO: Add quick starts, related vignettes, and implementation guidance.
{context_block}"""


def main() -> int:
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(description=__doc__)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--issue", help="GitHub issue number or URL; fetched with gh."
    )
    input_group.add_argument(
        "--issue-file", type=Path, help="Saved Markdown issue body."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Destination vignette.md (default derives from source and slug).",
    )
    parser.add_argument(
        "--new-pattern-slug",
        help="Slug for a selected new pattern; add it to patterns.yml separately.",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite an existing output file."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print the draft instead of writing it."
    )
    args = parser.parse_args()

    try:
        body = (
            args.issue_file.read_text(encoding="utf-8")
            if args.issue_file
            else _issue_body(args.issue)
        )
        values = _parse_issue_body(body)
        rendered = _render(values, args.new_pattern_slug)
        source = _identifier(values, "source")
        slug = _identifier(values, "slug")
        output = (
            args.output
            or REPO_ROOT / "docs" / "user-stories" / source / slug / "vignette.md"
        )
        if args.dry_run:
            print(rendered, end="")  # noqa: T201
        else:
            if output.exists() and not args.force:
                message = f"Refusing to overwrite {output}; use --force if intended."
                raise FileExistsError(message)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered, encoding="utf-8")
            _update_navigation(
                _required(values, "title"), _required(values, "implementer"), output
            )
            display_path = (
                output.relative_to(REPO_ROOT)
                if output.is_relative_to(REPO_ROOT)
                else output
            )
            print(f"Wrote {display_path}")  # noqa: T201
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)  # noqa: T201
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
