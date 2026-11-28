#!/usr/bin/env python3
"""Validate tracked Mermaid source files (.mmd)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple


DIAGRAM_KEYWORDS = (
    "graph",
    "flowchart",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "erDiagram",
    "gantt",
    "pie",
    "journey",
    "quadrantChart",
    "block-beta",
    "mindmap",
    "timeline",
    "gitGraph",
)
FENCE_MARKER = "```"
COMMENT_MARKER = "%%"
FRONT_MATTER_MARKER = "---"


@dataclass(frozen=True)
class Finding:
    kind: str
    path: str
    line: int
    message: str


def tracked_mmd_files(root: Path) -> List[str]:
    result = subprocess.run(
        ["git", "ls-files", "*.mmd"],
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )
    return sorted(name for name in result.stdout.splitlines() if name)


def content_lines(lines: List[str]) -> List[Tuple[int, str]]:
    """Return (line number, stripped text) for real content lines.

    Skips blank lines, %% comment lines, and one optional --- front-matter
    block when it opens on the first non-blank line and is closed later.
    """
    index = 0
    total = len(lines)
    while index < total and not lines[index].strip():
        index += 1
    if index < total and lines[index].strip() == FRONT_MATTER_MARKER:
        closing = index + 1
        while closing < total and lines[closing].strip() != FRONT_MATTER_MARKER:
            closing += 1
        if closing < total:
            index = closing + 1
    found: List[Tuple[int, str]] = []
    for offset in range(index, total):
        stripped = lines[offset].strip()
        if stripped and not stripped.startswith(COMMENT_MARKER):
            found.append((offset + 1, stripped))
    return found


def check_file(root: Path, relative: str) -> List[Finding]:
    raw = (root / relative).read_bytes()
    text = raw.decode("utf-8")
    lines = text.split("\n")
    findings: List[Finding] = []

    for number, line in enumerate(lines, start=1):
        if line.startswith(FENCE_MARKER):
            findings.append(
                Finding("fenced", relative, number, "line starts with a Markdown code fence")
            )

    crlf_line = next(
        (number for number, line in enumerate(lines, start=1) if line.endswith("\r")),
        None,
    )
    if crlf_line is not None:
        findings.append(
            Finding("crlf", relative, crlf_line, "file contains CRLF line endings")
        )

    if findings and any(f.kind == "fenced" for f in findings):
        return findings

    content = content_lines(lines)
    if not content:
        findings.append(
            Finding("empty", relative, 1, "no diagram content apart from blank or %% comment lines")
        )
    elif not content[0][1].startswith(DIAGRAM_KEYWORDS):
        findings.append(
            Finding(
                "no-diagram-keyword",
                relative,
                content[0][0],
                "first content line does not start with a known Mermaid diagram keyword",
            )
        )
    return findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=".",
        help="repository root used as cwd for `git ls-files '*.mmd'` (default: current directory)",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    findings: List[Finding] = []
    files = tracked_mmd_files(root)
    for relative in files:
        findings.extend(check_file(root, relative))

    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.kind}: {finding.message}")

    if findings:
        counts = {}
        for finding in findings:
            counts[finding.kind] = counts.get(finding.kind, 0) + 1
        summary = ", ".join(f"{kind}={counts[kind]}" for kind in sorted(counts))
        print(f"mermaid-sources: {len(findings)} findings ({summary}) in {len(files)} tracked .mmd files")
        return 1
    print(f"mermaid-sources: ok ({len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
