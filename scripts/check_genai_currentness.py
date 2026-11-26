#!/usr/bin/env python3
"""Validate GenAI volatile-claim currentness and GenAI HLD solution parity."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Sequence


GENAI_ROOT = Path("06-genai-systems")
GENAI_HLD_DIR = GENAI_ROOT / "02-llm-hld-projects"
GENAI_SOLUTIONS = Path("solutions")
CURRENTNESS_LEDGER = Path("resources/GENAI-CURRENTNESS-LEDGER.md")
INTERVIEW_DATA = Path("apps/portal/src/components/interview/interview-data.ts")
SOLUTIONS_README = Path("solutions/README.md")

CLAIM_TYPE_PATTERNS = {
    "context-window": re.compile(r"\bcontext[- ]?window\b", re.IGNORECASE),
    "model-surface": re.compile(
        r"\b("
        r"GPT-4(?:o(?:-mini)?|\.1|\.5)?|"
        r"GPT-3\.5|"
        r"OpenAI|"
        r"Anthropic|"
        r"Claude|"
        r"Gemini"
        r")\b",
        re.IGNORECASE,
    ),
    "pricing-cost": re.compile(r"\b(pricing|price|cost per|credits?)\b", re.IGNORECASE),
    "safety-product": re.compile(r"\b(moderation API|safety API|toxicity API)\b", re.IGNORECASE),
    "vector-backend": re.compile(r"\b(Pinecone|Weaviate)\b", re.IGNORECASE),
}
DATED_CAVEAT_RE = re.compile(r"\bAs of \d{4}-\d{2}-\d{2}\b")
ALLOWED_LEDGER_STATUSES = {"validated", "watchlist", "refresh-needed", "deferred"}
REQUIRED_LEDGER_COLUMNS = [
    "path",
    "claim_type",
    "claim_summary",
    "source_standard",
    "primary_source",
    "verified_on",
    "review_due",
    "status",
    "notes",
]


@dataclass(frozen=True)
class Finding:
    kind: str
    target: str
    path: str
    message: str


def relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def is_markdown_file(path: Path) -> bool:
    return path.is_file() and not path.is_symlink() and path.suffix.lower() == ".md"


def discover_genai_markdown(root: Path) -> list[Path]:
    paths: list[Path] = []
    base = root / GENAI_ROOT
    if base.is_dir() and not base.is_symlink():
        paths.extend(
            path
            for path in sorted(base.rglob("*.md"))
            if is_markdown_file(path) and path.name != "AGENTS.md"
        )

    solutions = root / GENAI_SOLUTIONS
    if solutions.is_dir() and not solutions.is_symlink():
        paths.extend(
            path for path in sorted(solutions.glob("genai-hld-*.md")) if is_markdown_file(path)
        )
    return paths


def discover_volatile_claim_groups(root: Path) -> list[tuple[str, str]]:
    volatile_claims: set[tuple[str, str]] = set()
    for path in discover_genai_markdown(root):
        for line in path.read_text(encoding="utf-8").splitlines():
            if DATED_CAVEAT_RE.search(line):
                continue
            for claim_type, pattern in CLAIM_TYPE_PATTERNS.items():
                if pattern.search(line):
                    volatile_claims.add((relative_path(root, path), claim_type))
    return sorted(volatile_claims)


def parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_currentness_ledger(root: Path) -> tuple[dict[str, list[dict[str, str]]], list[Finding], bool]:
    path = root / CURRENTNESS_LEDGER
    if not path.is_file() or path.is_symlink():
        return {}, [
            Finding(
                "missing-genai-currentness-ledger",
                "genai",
                str(CURRENTNESS_LEDGER),
                "resources/GENAI-CURRENTNESS-LEDGER.md is required when GenAI volatile claims are present",
            )
        ], False

    rows: dict[str, list[dict[str, str]]] = {}
    row_keys: set[tuple[str, str]] = set()
    findings: list[Finding] = []
    headers_seen = False

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "---" in stripped:
            continue
        cells = parse_table_cells(stripped)
        if [cell.lower() for cell in cells] == REQUIRED_LEDGER_COLUMNS:
            headers_seen = True
            continue
        if not headers_seen:
            continue
        if len(cells) != len(REQUIRED_LEDGER_COLUMNS):
            findings.append(
                Finding(
                    "malformed-genai-currentness-row",
                    str(CURRENTNESS_LEDGER),
                    f"{CURRENTNESS_LEDGER}:{line_number}",
                    "currentness ledger row must have 9 columns",
                )
            )
            continue

        row = dict(zip(REQUIRED_LEDGER_COLUMNS, cells))
        row_path = row["path"].strip().strip("`")
        row["path"] = row_path
        row["claim_type"] = row["claim_type"].strip().strip("`")
        if not row_path:
            findings.append(
                Finding(
                    "empty-genai-currentness-path",
                    str(CURRENTNESS_LEDGER),
                    f"{CURRENTNESS_LEDGER}:{line_number}",
                    "path is required",
                )
            )
            continue
        if row_path.startswith("/") or ".." in Path(row_path).parts or "\\" in row_path:
            findings.append(
                Finding(
                    "invalid-genai-currentness-path",
                    row_path,
                    f"{CURRENTNESS_LEDGER}:{line_number}",
                    "path must be a safe repository-relative path",
                )
            )
            continue
        for column in REQUIRED_LEDGER_COLUMNS[1:-1]:
            if not row[column]:
                findings.append(
                    Finding(
                        "incomplete-genai-currentness-row",
                        row_path,
                        f"{CURRENTNESS_LEDGER}:{line_number}",
                        f"{column} is required",
                    )
                )
        status = row["status"].lower()
        if status not in ALLOWED_LEDGER_STATUSES:
            findings.append(
                Finding(
                    "invalid-genai-currentness-status",
                    row_path,
                    f"{CURRENTNESS_LEDGER}:{line_number}",
                    f"status must be one of {', '.join(sorted(ALLOWED_LEDGER_STATUSES))}",
                )
            )
        elif status in {"refresh-needed", "deferred"}:
            findings.append(
                Finding(
                    "unresolved-genai-currentness-status",
                    row_path,
                    f"{CURRENTNESS_LEDGER}:{line_number}",
                    "refresh-needed and deferred rows cannot satisfy the currentness gate",
                )
            )
        verified_on = parse_date(row["verified_on"])
        review_due = parse_date(row["review_due"])
        today = date.today()
        if verified_on is None:
            findings.append(
                Finding(
                    "invalid-genai-currentness-date",
                    row_path,
                    f"{CURRENTNESS_LEDGER}:{line_number}",
                    "verified_on must be an ISO date",
                )
            )
        if review_due is None:
            findings.append(
                Finding(
                    "invalid-genai-currentness-date",
                    row_path,
                    f"{CURRENTNESS_LEDGER}:{line_number}",
                    "review_due must be an ISO date",
                )
            )
        if verified_on is not None and review_due is not None and verified_on > review_due:
            findings.append(
                Finding(
                    "invalid-genai-currentness-window",
                    row_path,
                    f"{CURRENTNESS_LEDGER}:{line_number}",
                    "verified_on must not be after review_due",
                )
            )
        if review_due is not None and review_due < today:
            findings.append(
                Finding(
                    "expired-genai-currentness-row",
                    row_path,
                    f"{CURRENTNESS_LEDGER}:{line_number}",
                    "review_due has passed; refresh the claim before passing currentness",
                )
            )
        row_key = (row_path, row["claim_type"])
        if row_key in row_keys:
            findings.append(
                Finding(
                    "duplicate-genai-currentness-row",
                    row_path,
                    f"{CURRENTNESS_LEDGER}:{line_number}",
                    "duplicate currentness ledger path and claim type",
                )
            )
            continue
        row_keys.add(row_key)
        rows.setdefault(row_path, []).append(row)

    if not headers_seen:
        findings.append(
            Finding(
                "malformed-genai-currentness-ledger",
                str(CURRENTNESS_LEDGER),
                str(CURRENTNESS_LEDGER),
                "ledger must include the expected 9-column header",
            )
        )

    return rows, findings, True


def discover_hld_projects(root: Path) -> list[str]:
    base = root / GENAI_HLD_DIR
    if not base.is_dir() or base.is_symlink():
        return []
    return [
        path.name
        for path in sorted(base.iterdir())
        if path.is_dir() and not path.is_symlink() and (path / "PROBLEM.md").is_file()
    ]


def interview_problem_array(text: str) -> str:
    marker = "INTERVIEW_PROBLEMS"
    start = text.find(marker)
    if start == -1:
        return ""
    initializer_start = text.find("=", start)
    if initializer_start == -1:
        return ""
    bracket_start = text.find("[", initializer_start)
    if bracket_start == -1:
        return ""

    depth = 0
    in_string = False
    quote = ""
    escaped = False
    for index in range(bracket_start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                in_string = False
            continue
        if char in ('"', "'", "`"):
            in_string = True
            quote = char
            continue
        if char == "[":
            depth += 1
            continue
        if char == "]":
            depth -= 1
            if depth == 0:
                return text[bracket_start + 1 : index]
    return ""


def parse_genai_hld_interviews(root: Path) -> tuple[dict[str, str], list[Finding]]:
    path = root / INTERVIEW_DATA
    if not path.is_file() or path.is_symlink():
        return {}, [
            Finding(
                "missing-interview-data",
                "genai-hld",
                str(INTERVIEW_DATA),
                "portal interview metadata is required",
            )
        ]

    array_text = interview_problem_array(path.read_text(encoding="utf-8"))
    entries: dict[str, str] = {}
    findings: list[Finding] = []
    for match in re.finditer(r"\{(?P<body>.*?)\}", array_text, re.DOTALL):
        body = match.group("body")
        if not re.search(r'type:\s*"genai-hld"', body):
            continue
        slug_match = re.search(r'slug:\s*"([^"]+)"', body)
        solution_match = re.search(r'solutionPath:\s*"([^"]+)"', body)
        if not slug_match:
            findings.append(
                Finding(
                    "missing-genai-hld-interview-slug",
                    "genai-hld",
                    str(INTERVIEW_DATA),
                    "GenAI HLD interview entry needs a slug",
                )
            )
            continue
        slug = slug_match.group(1)
        if not solution_match:
            findings.append(
                Finding(
                    "missing-genai-hld-solution-path",
                    slug,
                    str(INTERVIEW_DATA),
                    "GenAI HLD interview entry needs solutionPath",
                )
            )
            continue
        entries[slug] = solution_match.group(1)
    return entries, findings


def default_solution_path(slug: str) -> str:
    return f"solutions/genai-hld-{slug}.md"


def compare(root: Path) -> tuple[list[Finding], dict[str, int]]:
    volatile_claims = discover_volatile_claim_groups(root)
    findings: list[Finding] = []

    ledger_rows, ledger_findings, ledger_exists = parse_currentness_ledger(root)
    if volatile_claims or ledger_exists:
        findings.extend(ledger_findings)

    ledger_claims = {
        (row_path, row["claim_type"])
        for row_path, rows in ledger_rows.items()
        for row in rows
    }
    for path, claim_type in volatile_claims:
        if (path, claim_type) not in ledger_claims:
            findings.append(
                Finding(
                    "missing-genai-currentness-row",
                    f"{path}#{claim_type}",
                    str(CURRENTNESS_LEDGER),
                    "volatile GenAI claim needs a dated inline caveat or currentness ledger row",
                )
            )

    for row_path in sorted(ledger_rows):
        if not (root / row_path).is_file():
            findings.append(
                Finding(
                    "stale-genai-currentness-row",
                    row_path,
                    str(CURRENTNESS_LEDGER),
                    "ledger row has no matching GenAI file",
                )
            )

    hld_projects = discover_hld_projects(root)
    interviews, interview_findings = parse_genai_hld_interviews(root)
    findings.extend(interview_findings)

    solutions_readme = root / SOLUTIONS_README
    solutions_readme_text = ""
    if solutions_readme.is_file() and not solutions_readme.is_symlink():
        solutions_readme_text = solutions_readme.read_text(encoding="utf-8")

    for slug in hld_projects:
        solution_path = interviews.get(slug)
        if solution_path is None:
            findings.append(
                Finding(
                    "missing-genai-hld-interview-entry",
                    slug,
                    str(INTERVIEW_DATA),
                    "GenAI HLD project needs an Interview Mode entry",
                )
            )
            solution_path = default_solution_path(slug)

        solution_file = root / solution_path
        if not solution_file.is_file() or solution_file.is_symlink():
            findings.append(
                Finding(
                    "missing-genai-hld-solution-file",
                    slug,
                    solution_path,
                    "GenAI HLD interview solution file is required",
                )
            )

        solution_name = Path(solution_path).name
        if not solutions_readme_text or solution_name not in solutions_readme_text:
            findings.append(
                Finding(
                    "missing-solutions-readme-row",
                    slug,
                    str(SOLUTIONS_README),
                    "solutions README must list the GenAI HLD coach answer",
                )
            )

    summary = {
        "genai-volatile-claim-groups": len(volatile_claims),
        "genai-hld-interviews": len(hld_projects),
    }
    return findings, summary


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    findings, summary = compare(root)

    if args.format == "json":
        print(json.dumps({"ok": not findings, "summary": summary, "findings": [asdict(finding) for finding in findings]}, indent=2))
    else:
        print(
            "summary: "
            f"genai-volatile-claim-groups={summary['genai-volatile-claim-groups']} "
            f"genai-hld-interviews={summary['genai-hld-interviews']}"
        )
        for finding in findings:
            print(f"{finding.kind}: {finding.target}: {finding.path}: {finding.message}")
        if not findings:
            print("genai-currentness: ok")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
