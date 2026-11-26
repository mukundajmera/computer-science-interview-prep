#!/usr/bin/env python3
"""Validate HLD concept README catalog coverage against concept folders."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


HLD_DIR = Path("03-hld-concepts")
README_FILE = HLD_DIR / "README.md"
CATALOG_HEADING = "📚 Concept Catalog"
MAPPING_HEADING = "🔗 Concept → Project Mapping"
CHECKLIST_HEADING = "✅ Completion Checklist"
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CHECKBOX_RE = re.compile(r"^\s*-\s+\[[xX ]\]\s+(?P<body>.+?)\s*$")
COMPLETE_STATUSES = {"✅ Complete", "Complete"}


@dataclass(frozen=True)
class ConceptRow:
    slug: str
    display: str
    target: str
    path: str
    cells: tuple[str, ...]


@dataclass(frozen=True)
class Finding:
    kind: str
    slug: str
    path: str
    message: str


def is_visible_dir(path: Path) -> bool:
    return path.is_dir() and not path.is_symlink() and not path.name.startswith(".")


def has_complete_docs(path: Path) -> bool:
    return (
        (path / "THEORY.md").is_file()
        and not (path / "THEORY.md").is_symlink()
        and (path / "INTERVIEW-QA.md").is_file()
        and not (path / "INTERVIEW-QA.md").is_symlink()
    )


def discover_complete_concepts(root: Path) -> dict[str, Path]:
    base = root / HLD_DIR
    if not base.is_dir() or base.is_symlink():
        return {}
    return {
        directory.name: directory
        for directory in sorted(base.iterdir())
        if is_visible_dir(directory) and has_complete_docs(directory)
    }


def split_table_row(line: str) -> list[str]:
    cells = []
    current = []
    escaped = False
    for char in line.strip().strip("|"):
        if char == "|" and not escaped:
            cells.append("".join(current).replace("\\|", "|").strip())
            current = []
        else:
            current.append(char)
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
    cells.append("".join(current).replace("\\|", "|").strip())
    return cells


def is_separator_row(cells: Sequence[str]) -> bool:
    return all(cell and set(cell) <= {"-", ":"} for cell in cells)


def section_lines(markdown: str, heading: str) -> list[tuple[int, str]]:
    lines = markdown.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == f"## {heading}":
            start = index + 1
            break
    if start is None:
        return []

    result = []
    for index in range(start, len(lines)):
        line = lines[index]
        if line.startswith("## "):
            break
        result.append((index + 1, line))
    return result


def markdown_link(cell: str) -> tuple[str, str] | None:
    match = LINK_RE.search(cell)
    if not match:
        return None
    return match.group(1).strip(), match.group(2).strip()


def local_concept_slug(target: str) -> str | None:
    target = target.split("#", 1)[0].split("?", 1)[0].strip()
    if not target.startswith("./"):
        return None
    relative = target[2:].strip("/")
    if not relative:
        return None
    parts = relative.split("/")
    slug = parts[0]
    if slug in {"", ".", ".."} or slug.startswith("."):
        return None
    if len(parts) == 1:
        return slug
    if len(parts) == 2 and parts[1] in {"THEORY.md", "INTERVIEW-QA.md", "README.md"}:
        return slug
    return None


def parse_table_rows(
    markdown: str,
    heading: str,
    minimum_columns: int,
    finding_kind: str,
) -> tuple[dict[str, ConceptRow], list[Finding]]:
    rows: dict[str, ConceptRow] = {}
    findings: list[Finding] = []
    for line_number, line in section_lines(markdown, heading):
        if not line.strip().startswith("|"):
            continue
        cells = split_table_row(line)
        if not cells or is_separator_row(cells) or cells[0].lower() == "concept":
            continue
        if len(cells) < minimum_columns:
            findings.append(
                Finding(
                    finding_kind,
                    "<unknown>",
                    f"{README_FILE}:{line_number}",
                    f"{heading} row must have at least {minimum_columns} columns",
                )
            )
            continue
        link = markdown_link(cells[0])
        if link is None:
            findings.append(
                Finding(
                    finding_kind,
                    cells[0] or "<unknown>",
                    f"{README_FILE}:{line_number}",
                    "first table cell must link the concept name",
                )
            )
            continue
        display, target = link
        slug = local_concept_slug(target)
        if slug is None:
            continue
        if slug in rows:
            findings.append(
                Finding(
                    f"duplicate-{finding_kind.removeprefix('malformed-').removesuffix('-row')}-row",
                    slug,
                    f"{README_FILE}:{line_number}",
                    f"duplicate local concept link for {slug}",
                )
            )
            continue
        rows[slug] = ConceptRow(
            slug=slug,
            display=display,
            target=target,
            path=f"{README_FILE}:{line_number}",
            cells=tuple(cells),
        )
    return rows, findings


def parse_catalog_displays(markdown: str) -> set[str]:
    displays: set[str] = set()
    for _, line in section_lines(markdown, CATALOG_HEADING):
        if not line.strip().startswith("|"):
            continue
        cells = split_table_row(line)
        if not cells or is_separator_row(cells) or cells[0].lower() == "concept":
            continue
        link = markdown_link(cells[0])
        if link is None:
            continue
        displays.add(strip_inline_markdown(link[0]))
    return displays


def catalog_quality_findings(rows: dict[str, ConceptRow]) -> list[Finding]:
    findings: list[Finding] = []
    for slug, row in rows.items():
        if len(row.cells) < 4:
            continue
        what_it_solves, related, status = row.cells[1], row.cells[2], row.cells[3]
        if not what_it_solves or not related:
            findings.append(
                Finding(
                    "malformed-catalog-row",
                    slug,
                    row.path,
                    "catalog row must include non-empty problem and related-concept cells",
                )
            )
        if status.strip() not in COMPLETE_STATUSES:
            findings.append(
                Finding(
                    "invalid-catalog-status",
                    slug,
                    row.path,
                    "complete local concept rows must use a recognized complete status",
                )
            )
    return findings


def strip_inline_markdown(text: str) -> str:
    return text.replace("**", "").replace("`", "").strip()


def parse_checklist(
    markdown: str,
    catalog_rows: dict[str, ConceptRow],
    catalog_displays: set[str],
) -> tuple[set[str], list[Finding]]:
    display_to_slug = {row.display: slug for slug, row in catalog_rows.items()}
    slugs: set[str] = set()
    findings: list[Finding] = []
    for line_number, line in section_lines(markdown, CHECKLIST_HEADING):
        match = CHECKBOX_RE.match(line)
        if not match:
            continue
        body = match.group("body")
        link = markdown_link(body)
        if link is not None:
            display = strip_inline_markdown(link[0])
            slug = local_concept_slug(link[1])
            if slug is not None:
                if slug in catalog_rows:
                    slugs.add(slug)
                else:
                    findings.append(
                        Finding(
                            "extra-checklist-item",
                            display or slug,
                            f"{README_FILE}:{line_number}",
                            "checklist item links to a local concept not present in README catalog",
                        )
                    )
                continue
        else:
            display = strip_inline_markdown(body)
        slug = display_to_slug.get(display)
        if slug is not None:
            slugs.add(slug)
            continue
        if display in catalog_displays:
            continue
        findings.append(
            Finding(
                "extra-checklist-item",
                display or "<unknown>",
                f"{README_FILE}:{line_number}",
                "checklist item is not present in README catalog",
            )
        )
    return slugs, findings


def compare_catalog(root: Path) -> tuple[list[Finding], int]:
    expected = discover_complete_concepts(root)
    readme_path = root / README_FILE
    if not readme_path.is_file() or readme_path.is_symlink():
        return (
            [Finding("missing-readme", "<readme>", str(README_FILE), "HLD README is required")],
            len(expected),
        )

    markdown = readme_path.read_text(encoding="utf-8")
    catalog_rows, findings = parse_table_rows(markdown, CATALOG_HEADING, 4, "malformed-catalog-row")
    catalog_displays = parse_catalog_displays(markdown)
    mapping_rows, mapping_findings = parse_table_rows(markdown, MAPPING_HEADING, 2, "malformed-mapping-row")
    findings.extend(mapping_findings)
    findings.extend(catalog_quality_findings(catalog_rows))
    checklist, checklist_findings = parse_checklist(markdown, catalog_rows, catalog_displays)
    findings.extend(checklist_findings)

    for slug in sorted(expected):
        path = str(HLD_DIR / slug)
        if slug not in catalog_rows:
            findings.append(
                Finding("missing-catalog-row", slug, path, "complete HLD concept is not in README catalog")
            )
        if slug not in mapping_rows:
            findings.append(
                Finding(
                    "missing-mapping-row",
                    slug,
                    path,
                    "complete HLD concept is not in concept-to-project mapping",
                )
            )
        if slug not in checklist:
            findings.append(
                Finding(
                    "missing-checklist-item",
                    slug,
                    path,
                    "complete HLD concept is not in completion checklist",
                )
            )

    for slug, row in catalog_rows.items():
        directory = root / HLD_DIR / slug
        if slug not in expected and not is_visible_dir(directory):
            findings.append(
                Finding("extra-catalog-row", slug, row.path, "catalog row has no matching concept directory")
            )
    for slug, row in mapping_rows.items():
        directory = root / HLD_DIR / slug
        if slug not in expected and not is_visible_dir(directory):
            findings.append(
                Finding("extra-mapping-row", slug, row.path, "mapping row has no matching concept directory")
            )

    return sorted(findings, key=lambda item: (item.kind, item.slug, item.path)), len(expected)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    return parser.parse_args(argv)


def print_text(findings: list[Finding], total: int) -> None:
    print(f"summary: hld-concepts={total}")
    if findings:
        for finding in findings:
            print(f"{finding.kind}: {finding.slug} ({finding.path}; {finding.message})")
        return
    print("hld-concept-catalog: ok")


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    findings, total = compare_catalog(root)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "ok": not findings,
                    "summary": {"hld-concepts": total},
                    "findings": [asdict(finding) for finding in findings],
                },
                sort_keys=True,
            )
        )
    else:
        print_text(findings, total)

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
