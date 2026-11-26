#!/usr/bin/env python3
"""Validate LLD project coverage matrix against repository structure."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


LLD_DIR = Path("02-lld-projects")
MATRIX_FILE = LLD_DIR / "lld-doc-coverage-matrix.md"
README_FILE = LLD_DIR / "README.md"
CORE_DOCS = ("PROBLEM.md", "APPROACH.md", "DESIGN.md", "CODE-WALKTHROUGH.md")
ROW_RE = re.compile(r"^\|\s*\[(?P<slug>[^\]]+)\]\(\./(?P=slug)/\)\s*\|")
README_TOTAL_RE = re.compile(r"^\s*-\s*\*\*Total projects:\*\*\s*(?P<count>\d+)")
README_ROW_RE = re.compile(r"^\|\s*\[[^\]]+\]\(\./(?P<slug>[^/]+)/\)\s*\|")


@dataclass(frozen=True)
class Coverage:
    slug: str
    core_docs: str
    rubric: str
    pitfalls: str
    follow_ups: str
    java_v1: str
    java_v2: str
    java_v3: str
    java_tests: str
    python_v1: str
    python_v2: str
    python_v3: str
    python_tests: str


@dataclass(frozen=True)
class Finding:
    kind: str
    path: str
    message: str


def yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def has_direct_files(directory: Path, pattern: str) -> bool:
    return directory.is_dir() and any(path.is_file() for path in directory.glob(pattern))


def has_recursive_files(directory: Path, pattern: str) -> bool:
    return directory.is_dir() and any(path.is_file() for path in directory.glob(f"**/{pattern}"))


def discover_projects(root: Path) -> dict[str, Coverage]:
    base = root / LLD_DIR
    coverage: dict[str, Coverage] = {}
    if not base.is_dir() or base.is_symlink():
        return coverage

    for project_dir in sorted(path for path in base.iterdir() if path.is_dir() and not path.is_symlink()):
        if not (project_dir / "PROBLEM.md").is_file():
            continue
        slug = project_dir.name
        coverage[slug] = Coverage(
            slug=slug,
            core_docs=yes_no(all((project_dir / doc).is_file() for doc in CORE_DOCS)),
            rubric=yes_no((project_dir / "RUBRIC.md").is_file()),
            pitfalls=yes_no((project_dir / "PITFALLS.md").is_file()),
            follow_ups=yes_no((project_dir / "FOLLOW-UPS.md").is_file()),
            java_v1=yes_no(has_direct_files(project_dir / "java" / "v1-basic", "*.java")),
            java_v2=yes_no(has_direct_files(project_dir / "java" / "v2-extended", "*.java")),
            java_v3=yes_no(has_direct_files(project_dir / "java" / "v3-optimized", "*.java")),
            java_tests=yes_no(has_recursive_files(project_dir / "java" / "tests", "*.java")),
            python_v1=yes_no(has_direct_files(project_dir / "python" / "v1-basic", "*.py")),
            python_v2=yes_no(has_direct_files(project_dir / "python" / "v2-extended", "*.py")),
            python_v3=yes_no(has_direct_files(project_dir / "python" / "v3-optimized", "*.py")),
            python_tests=yes_no(has_recursive_files(project_dir / "python" / "tests", "*.py")),
        )
    return coverage


def parse_matrix(root: Path) -> tuple[dict[str, Coverage], list[Finding]]:
    path = root / MATRIX_FILE
    findings: list[Finding] = []
    rows: dict[str, Coverage] = {}
    if not path.is_file() or path.is_symlink():
        return rows, [Finding("missing-matrix", str(MATRIX_FILE), "LLD coverage matrix is required")]

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = ROW_RE.match(line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 13:
            findings.append(
                Finding(
                    "malformed-matrix-row",
                    f"{MATRIX_FILE}:{line_number}",
                    "LLD coverage row must have 13 columns",
                )
            )
            continue
        slug = match.group("slug")
        if slug in rows:
            findings.append(
                Finding("duplicate-matrix-row", f"{MATRIX_FILE}:{line_number}", f"duplicate row for {slug}")
            )
            continue
        rows[slug] = Coverage(
            slug=slug,
            core_docs=cells[1],
            rubric=cells[2],
            pitfalls=cells[3],
            follow_ups=cells[4],
            java_v1=cells[5],
            java_v2=cells[6],
            java_v3=cells[7],
            java_tests=cells[8],
            python_v1=cells[9],
            python_v2=cells[10],
            python_v3=cells[11],
            python_tests=cells[12],
        )
    return rows, findings


def parse_readme(root: Path) -> tuple[Optional[int], list[str], list[Finding]]:
    path = root / README_FILE
    findings: list[Finding] = []
    slugs: list[str] = []
    total_count: Optional[int] = None

    if not path.is_file() or path.is_symlink():
        return None, slugs, [Finding("missing-readme", str(README_FILE), "LLD README is required")]

    seen_slugs: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        total_match = README_TOTAL_RE.match(line)
        if total_match:
            total_count = int(total_match.group("count"))
            continue

        row_match = README_ROW_RE.match(line)
        if row_match:
            slug = row_match.group("slug")
            if slug in seen_slugs:
                findings.append(
                    Finding("duplicate-readme-row", f"{README_FILE}:{line_number}", f"duplicate row for {slug}")
                )
            else:
                seen_slugs.add(slug)
                slugs.append(slug)

    return total_count, slugs, findings


def compare_coverage(root: Path) -> tuple[list[Finding], int]:
    expected = discover_projects(root)
    actual, findings = parse_matrix(root)

    for slug, expected_row in expected.items():
        actual_row = actual.get(slug)
        path = str(LLD_DIR / slug)
        if actual_row is None:
            findings.append(
                Finding("missing-matrix-row", path, "LLD project is not represented in coverage matrix")
            )
            continue
        for field in (
            "core_docs",
            "rubric",
            "pitfalls",
            "follow_ups",
            "java_v1",
            "java_v2",
            "java_v3",
            "java_tests",
            "python_v1",
            "python_v2",
            "python_v3",
            "python_tests",
        ):
            expected_value = getattr(expected_row, field)
            actual_value = getattr(actual_row, field)
            if actual_value != expected_value:
                findings.append(
                    Finding(
                        "stale-matrix-cell",
                        path,
                        f"{field} is {actual_value!r}, expected {expected_value!r}",
                    )
                )

    for slug in actual:
        if slug not in expected:
            findings.append(
                Finding("extra-matrix-row", str(MATRIX_FILE), f"matrix row has no matching LLD project: {slug}")
            )

    readme_total, readme_slugs, readme_findings = parse_readme(root)
    findings.extend(readme_findings)

    if readme_total is not None and readme_total != len(expected):
        findings.append(
            Finding("stale-readme-count", str(README_FILE), f"Total projects is {readme_total}, expected {len(expected)}")
        )

    readme_slug_set = set(readme_slugs)

    for slug in expected:
        if slug not in readme_slug_set:
            findings.append(
                Finding("missing-readme-row", str(README_FILE), f"LLD project is not represented in README: {slug}")
            )

    for slug in readme_slugs:
        if slug not in expected:
            findings.append(
                Finding("extra-readme-row", str(README_FILE), f"README row has no matching LLD project: {slug}")
            )

    return findings, len(expected)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    findings, total = compare_coverage(root)

    print(f"summary: lld-projects={total}")
    if findings:
        for finding in findings:
            print(f"{finding.kind}: {finding.path}: {finding.message}")
        return 1

    print("lld-project-coverage: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
