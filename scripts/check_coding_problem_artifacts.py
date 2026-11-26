#!/usr/bin/env python3
"""Reject generated artifacts under coding problem bank support paths."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Sequence


CHECK_ROOTS = (
    Path("05-coding-problems"),
    Path("resources"),
    Path("scripts"),
)
PROBLEM_BANK_DIR = Path("05-coding-problems/problem-bank")
BLOCKED_PARTS = {"__pycache__", ".pytest_cache"}
BLOCKED_NAMES = {"Driver.java", "payload.json", "result.json"}
BLOCKED_SUFFIXES = {".pyc", ".class"}
INDENTED_README_PATTERN = re.compile(r"^ {4}(?:#|\||- )", re.MULTILINE)


def generated_artifacts(root: Path) -> list[Path]:
    findings: list[Path] = []
    for relative_root in CHECK_ROOTS:
        base = root / relative_root
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_dir():
                continue
            relative = path.relative_to(root)
            if is_blocked_artifact(relative):
                findings.append(relative)
    return sorted(findings)


def is_blocked_artifact(relative: Path) -> bool:
    if any(part in BLOCKED_PARTS for part in relative.parts):
        return True
    if relative.name in BLOCKED_NAMES:
        return True
    return relative.suffix in BLOCKED_SUFFIXES


def indented_problem_readmes(root: Path) -> list[Path]:
    problem_bank = root / PROBLEM_BANK_DIR
    if not problem_bank.exists():
        return []
    findings: list[Path] = []
    for readme in problem_bank.glob("lc-*/README.md"):
        text = readme.read_text(encoding="utf-8")
        if INDENTED_README_PATTERN.search(text):
            findings.append(readme.relative_to(root))
    return sorted(findings)


def main(argv: Sequence[str] | None = None) -> int:
    root = Path(argv[0] if argv else ".").resolve()
    artifact_findings = generated_artifacts(root)
    readme_findings = indented_problem_readmes(root)
    for finding in artifact_findings:
        print(finding)
    for finding in readme_findings:
        print(f"{finding}: problem README appears accidentally indented as a code block")
    if artifact_findings or readme_findings:
        return 1
    print("coding-problem-artifacts: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
