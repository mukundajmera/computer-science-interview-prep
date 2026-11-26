#!/usr/bin/env python3
"""Validate that the git worktree is safe to checkpoint.

This checker is intentionally path/status-only. It never opens changed files,
which keeps raw source areas such as temp_upload out of the validation path.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


TEMP_UPLOAD_PREFIX = "temp_upload/"


class BoundaryError(Exception):
    """Raised for user-facing checkpoint boundary failures."""


@dataclass(frozen=True)
class StatusEntry:
    status: str
    path: str
    original_path: str = ""


@dataclass(frozen=True)
class Finding:
    kind: str
    status: str
    path: str
    message: str


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root. Defaults to this script's parent repository.",
    )
    parser.add_argument(
        "--format",
        choices=("summary", "json"),
        default="summary",
        help="Output format.",
    )
    parser.add_argument(
        "--max-findings",
        default=40,
        type=int,
        help="Maximum findings to print in summary mode. Use 0 to print all findings.",
    )
    return parser.parse_args(argv)


def run_git_status(root: Path) -> bytes:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise BoundaryError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def parse_porcelain_v1_z(output: bytes) -> list[StatusEntry]:
    entries: list[StatusEntry] = []
    fields = [field for field in output.split(b"\0") if field]
    index = 0
    while index < len(fields):
        field = fields[index].decode("utf-8", errors="replace")
        if len(field) < 4 or field[2] != " ":
            raise BoundaryError(f"unexpected git status record: {field!r}")
        status = field[:2]
        path = field[3:]
        original_path = ""
        index += 1
        if status[0] in {"R", "C"}:
            if index >= len(fields):
                raise BoundaryError(f"missing source path for git status record: {field!r}")
            original_path = fields[index].decode("utf-8", errors="replace")
            index += 1
        entries.append(StatusEntry(status=status, path=path, original_path=original_path))
    return entries


def is_temp_upload_path(path: str) -> bool:
    return path == "temp_upload" or path.startswith(TEMP_UPLOAD_PREFIX)


def has_index_change(status: str) -> bool:
    return status[0] not in {" ", "?", "!"}


def has_worktree_change(status: str) -> bool:
    return status[1] not in {" ", "?", "!"}


def is_unmerged(status: str) -> bool:
    return "U" in status or status in {"AA", "DD"}


def classify_entry(entry: StatusEntry) -> list[Finding]:
    findings: list[Finding] = []
    paths = [entry.path]
    if entry.original_path:
        paths.append(entry.original_path)

    for path in paths:
        if is_temp_upload_path(path):
            findings.append(
                Finding(
                    kind="raw-source-dirty",
                    status=entry.status,
                    path=path,
                    message="temp_upload path is dirty; exclude or resolve before checkpoint",
                )
            )

    if entry.status == "??":
        findings.append(
            Finding(
                kind="untracked-file",
                status=entry.status,
                path=entry.path,
                message="untracked file would be omitted from a staged checkpoint",
            )
        )
        return findings

    if is_unmerged(entry.status):
        findings.append(
            Finding(
                kind="unmerged-path",
                status=entry.status,
                path=entry.path,
                message="resolve merge conflict before checkpoint",
            )
        )
    elif has_index_change(entry.status) and has_worktree_change(entry.status):
        findings.append(
            Finding(
                kind="mixed-index-worktree",
                status=entry.status,
                path=entry.path,
                message="path has both staged and unstaged changes",
            )
        )
    elif has_worktree_change(entry.status):
        findings.append(
            Finding(
                kind="unstaged-change",
                status=entry.status,
                path=entry.path,
                message="unstaged change would be omitted from a staged checkpoint",
            )
        )

    return findings


def collect_findings(entries: Sequence[StatusEntry]) -> list[Finding]:
    findings: list[Finding] = []
    for entry in entries:
        findings.extend(classify_entry(entry))
    return findings


def print_summary(findings: Sequence[Finding], max_findings: int) -> None:
    if not findings:
        print("checkpoint-boundary: ok")
        return
    counts = Counter(finding.kind for finding in findings)
    count_text = ", ".join(f"{kind}={count}" for kind, count in sorted(counts.items()))
    print(f"checkpoint-boundary: failed (findings={len(findings)}; {count_text})", file=sys.stderr)
    visible_findings = findings if max_findings <= 0 else findings[:max_findings]
    for finding in visible_findings:
        print(
            f"checkpoint-boundary: {finding.kind} {finding.status} {finding.path}: {finding.message}",
            file=sys.stderr,
        )
    omitted = len(findings) - len(visible_findings)
    if omitted > 0:
        print(
            f"checkpoint-boundary: omitted {omitted} additional findings; rerun with --max-findings 0 or --format json",
            file=sys.stderr,
        )


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = args.root.resolve()
    try:
        entries = parse_porcelain_v1_z(run_git_status(root))
        findings = collect_findings(entries)
    except BoundaryError as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.format == "json":
        print(
            json.dumps(
                {
                    "ok": not findings,
                    "findings": [asdict(finding) for finding in findings],
                    "finding_count": len(findings),
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print_summary(findings, args.max_findings)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
