#!/usr/bin/env python3
"""Validate executable sample inventory for non-LLD concept code."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


INVENTORY = Path("resources/executable-sample-inventory.md")
SAMPLE_ROOTS = (Path("00-theory"), Path("03-hld-concepts"), Path("06-genai-systems/00-concepts"))
VALID_STATUSES = {"tested", "illustrative-only", "move-to-lld"}
ROW_RE = re.compile(r"^\|\s*`(?P<path>[^`]+)`\s*\|\s*(?P<status>[^|]+?)\s*\|")


@dataclass(frozen=True)
class Sample:
    path: str
    expected_status: str
    evidence: str


@dataclass(frozen=True)
class Finding:
    kind: str
    path: str
    message: str


def is_sample_file(path: Path) -> bool:
    return (
        path.is_file()
        and path.suffix in {".java", ".py"}
        and "tests" not in path.parts
        and "__pycache__" not in path.parts
        and path.name != "__init__.py"
    )


def same_language_tests_exist(root: Path, path: Path) -> bool:
    parts = path.parts
    if "java" in parts:
        language = "java"
        pattern = "*.java"
    elif "python" in parts:
        language = "python"
        pattern = "*.py"
    else:
        return False
    language_index = parts.index(language)
    concept_dir = Path(*parts[:language_index])
    tests_dir = root / concept_dir / language / "tests"
    return tests_dir.is_dir() and any(candidate.is_file() for candidate in tests_dir.glob(f"**/{pattern}"))


def discover_samples(root: Path) -> dict[str, Sample]:
    samples: dict[str, Sample] = {}
    for relative_root in SAMPLE_ROOTS:
        directory = root / relative_root
        if not directory.is_dir() or directory.is_symlink():
            continue
        for path in sorted(directory.rglob("*")):
            if not is_sample_file(path):
                continue
            relative_path = path.relative_to(root).as_posix()
            tested = same_language_tests_exist(root, path.relative_to(root))
            samples[relative_path] = Sample(
                path=relative_path,
                expected_status="tested" if tested else "illustrative-only",
                evidence="Same-language test suite present."
                if tested
                else "No same-language test suite present.",
            )
    return samples


def parse_inventory(root: Path) -> tuple[dict[str, str], list[Finding]]:
    path = root / INVENTORY
    findings: list[Finding] = []
    rows: dict[str, str] = {}
    if not path.is_file() or path.is_symlink():
        return rows, [Finding("missing-inventory", str(INVENTORY), "executable sample inventory is required")]

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = ROW_RE.match(line)
        if not match:
            continue
        sample_path = match.group("path")
        status = match.group("status").strip()
        if status not in VALID_STATUSES:
            findings.append(
                Finding(
                    "invalid-status",
                    f"{INVENTORY}:{line_number}",
                    f"{sample_path} uses invalid status {status!r}",
                )
            )
        if sample_path in rows:
            findings.append(
                Finding(
                    "duplicate-inventory-row",
                    f"{INVENTORY}:{line_number}",
                    f"duplicate row for {sample_path}",
                )
            )
            continue
        rows[sample_path] = status
    return rows, findings


def compare_inventory(root: Path) -> tuple[list[Finding], int]:
    expected = discover_samples(root)
    actual, findings = parse_inventory(root)

    for path, sample in expected.items():
        actual_status = actual.get(path)
        if actual_status is None:
            findings.append(
                Finding("missing-inventory-row", path, "executable sample path is not represented")
            )
            continue
        if actual_status != "move-to-lld" and actual_status != sample.expected_status:
            findings.append(
                Finding(
                    "stale-status",
                    path,
                    f"status is {actual_status!r}, expected {sample.expected_status!r}",
                )
            )

    for path in actual:
        if path not in expected:
            findings.append(
                Finding("extra-inventory-row", path, "inventory row has no matching executable sample")
            )
    return findings, len(expected)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    findings, total = compare_inventory(root)

    print(f"summary: executable-samples={total}")
    if findings:
        for finding in findings:
            print(f"{finding.kind}: {finding.path}: {finding.message}")
        return 1

    print("executable-sample-inventory: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
