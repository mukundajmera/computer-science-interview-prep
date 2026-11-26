#!/usr/bin/env python3
"""Validate HLD project design docs against interview-readiness signals."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


HLD_DIR = Path("04-hld-projects")
REQUIRED_DOCS = ("PROBLEM.md", "APPROACH.md", "DESIGN.md", "RUBRIC.md", "PITFALLS.md", "FOLLOW-UPS.md", "STRONG-ANSWER.md")
PLACEHOLDER_TERMS = ("DomainRecord", "Domain Service", "ReadModel")
API_PATTERNS = (
    re.compile(r"^#{2,4}\s+.*\bAPI\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\s+/[A-Za-z0-9_/{}/:-]+"),
)
DATA_PATTERNS = (
    re.compile(r"^#{2,4}\s+.*\b(Data Model|Schema|Storage Model|Tables?)\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"\b(partition|index|primary key|retention|consistency)\b", re.IGNORECASE),
)
CAPACITY_RE = re.compile(r"\b(capacity|qps|rps|tps|throughput|peak|p95|p99|latency|availability|storage)\b", re.IGNORECASE)
FAILURE_RE = re.compile(r"\b(failure|recovery|retry|replay|rollback|degrad|backfill|dlq|timeout)\b", re.IGNORECASE)
STRONG_ANSWER_RE = re.compile(r"\b(STRONG-ANSWER\.md|strong answer|60-90|90 second|time-boxed)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    kind: str
    slug: str
    path: str
    message: str


def is_project_dir(path: Path) -> bool:
    return path.is_dir() and not path.is_symlink() and (path / "PROBLEM.md").is_file()


def discover_projects(root: Path) -> list[str]:
    base = root / HLD_DIR
    if not base.is_dir() or base.is_symlink():
        return []
    return [path.name for path in sorted(base.iterdir()) if is_project_dir(path)]


def has_any_pattern(text: str, patterns: Iterable[re.Pattern[str]]) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def project_findings(root: Path, slug: str) -> list[Finding]:
    project_dir = root / HLD_DIR / slug
    findings: list[Finding] = []
    if not is_project_dir(project_dir):
        return [Finding("missing-project", slug, str(HLD_DIR / slug), "HLD project directory with PROBLEM.md is required")]

    for doc in REQUIRED_DOCS:
        path = project_dir / doc
        if not path.is_file() or path.is_symlink():
            findings.append(Finding("missing-doc", slug, str(HLD_DIR / slug / doc), f"{doc} is required"))

    design_path = project_dir / "DESIGN.md"
    if not design_path.is_file() or design_path.is_symlink():
        return findings

    design = design_path.read_text(encoding="utf-8")
    for term in PLACEHOLDER_TERMS:
        if term in design:
            findings.append(
                Finding(
                    "placeholder-term",
                    slug,
                    str(HLD_DIR / slug / "DESIGN.md"),
                    f"replace generic placeholder term {term!r} with project-specific language",
                )
            )

    if not has_any_pattern(design, API_PATTERNS):
        findings.append(Finding("missing-api", slug, str(HLD_DIR / slug / "DESIGN.md"), "DESIGN.md needs API contracts or endpoint examples"))
    if not has_any_pattern(design, DATA_PATTERNS):
        findings.append(Finding("missing-data-model", slug, str(HLD_DIR / slug / "DESIGN.md"), "DESIGN.md needs data model, schema, indexes, partitioning, or retention details"))
    if not CAPACITY_RE.search(design):
        findings.append(Finding("missing-capacity", slug, str(HLD_DIR / slug / "DESIGN.md"), "DESIGN.md needs capacity, latency, throughput, or availability assumptions"))
    if not FAILURE_RE.search(design):
        findings.append(Finding("missing-failure-path", slug, str(HLD_DIR / slug / "DESIGN.md"), "DESIGN.md needs failure, recovery, retry, replay, or rollback handling"))

    problem = (project_dir / "PROBLEM.md").read_text(encoding="utf-8") if (project_dir / "PROBLEM.md").is_file() else ""
    strong = (project_dir / "STRONG-ANSWER.md").read_text(encoding="utf-8") if (project_dir / "STRONG-ANSWER.md").is_file() else ""
    if not STRONG_ANSWER_RE.search(design + "\n" + problem + "\n" + strong):
        findings.append(
            Finding(
                "missing-strong-answer",
                slug,
                str(HLD_DIR / slug),
                "project needs a strong-answer link, section, or time-boxed answer",
            )
        )

    return findings


def select_slugs(root: Path, args: argparse.Namespace) -> list[str]:
    discovered = discover_projects(root)
    if args.only:
        return list(args.only)
    if args.all:
        return discovered
    return discovered


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    parser.add_argument("--only", nargs="+", help="Specific project slugs to check.")
    parser.add_argument("--all", action="store_true", help="Check every discovered HLD project.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    slugs = select_slugs(root, args)
    findings: list[Finding] = []
    for slug in slugs:
        findings.extend(project_findings(root, slug))

    if args.format == "json":
        print(json.dumps({"summary": {"hld_projects": len(slugs), "findings": len(findings)}, "findings": [asdict(finding) for finding in findings]}, indent=2))
    else:
        print(f"summary: hld-projects={len(slugs)}")
        for finding in findings:
            print(f"{finding.kind}: {finding.path}: {finding.message}")
        if not findings:
            print("hld-project-readiness: ok")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
