#!/usr/bin/env python3
"""Validate the coding problem bank catalog and source manifests."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from coding_catalog.driver import java_toolchain_error, run_problem_drivers, validate_driver_generation
from coding_catalog.load import load_catalog, load_source_manifests
from coding_catalog.schema import COMPLETED_STATUSES, Finding, validate_catalog, validate_source_manifests


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate coding problem catalog contracts.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--strict", action="store_true", help="Validate catalog and sources strictly.")
    parser.add_argument("--sources", action="store_true", help="Validate source manifests only.")
    parser.add_argument("--collection", help="Restrict source validation to one collection id.")
    parser.add_argument(
        "--driver-generation",
        action="store_true",
        help="Validate generated driver source without executing repository solution code.",
    )
    parser.add_argument("--drivers", action="store_true", help="Run generated solution drivers.")
    parser.add_argument(
        "--allow-unsafe-driver-execution",
        action="store_true",
        help="Acknowledge that drivers execute repository solution code.",
    )
    parser.add_argument("--problem", help="Canonical problem id for driver execution. Defaults to all solution-bearing problems.")
    parser.add_argument("--language", choices=("java", "python"), help="Driver language to execute.")
    return parser.parse_args(argv)


def print_findings(findings: list[Finding]) -> None:
    for finding in findings:
        print(f"{finding.severity.upper()} {finding.path}: {finding.message}")


def has_errors(findings: list[Finding]) -> bool:
    return any(finding.severity == "error" for finding in findings)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.root).resolve()
    findings: list[Finding] = []

    if args.driver_generation:
        findings, count = validate_driver_generation(root, args.problem)
        print_findings(findings)
        if has_errors(findings):
            return 1
        print(f"PASS driver generation {count} problem(s)")
        return 0

    if args.drivers:
        if not args.allow_unsafe_driver_execution:
            print("--drivers requires --allow-unsafe-driver-execution", file=sys.stderr)
            return 2
        if not args.language:
            print("--drivers requires --language", file=sys.stderr)
            return 2
        if args.language == "java" and not args.problem:
            toolchain_error = java_toolchain_error()
            if toolchain_error is not None:
                findings.append(
                    Finding(
                        "error",
                        str(root / "05-coding-problems" / "problem-bank"),
                        toolchain_error,
                    )
                )
                print_findings(findings)
                return 1
        problem_ids = [args.problem] if args.problem else driver_problem_ids(root)
        for problem_id in problem_ids:
            findings.extend(
                run_problem_drivers(
                    root,
                    problem_id,
                    args.language,
                    allow_unsafe_driver_execution=True,
                )
            )
        print_findings(findings)
        if has_errors(findings):
            return 1
        print(f"PASS drivers {args.language} {len(problem_ids)} problem(s)")
        return 0

    if args.sources or args.strict:
        manifests = load_source_manifests(root, collection=args.collection)
        if args.collection and not manifests:
            findings.append(
                Finding(
                    "error",
                    str(root / "resources/source-intake/coding-lists" / f"{args.collection}.json"),
                    f"source manifest for collection {args.collection} is missing",
                )
            )
        findings.extend(
            validate_source_manifests(
                manifests,
                strict=args.strict,
                collection=args.collection,
            )
        )

    if not args.sources:
        findings.extend(validate_catalog(load_catalog(root), root, require_source_manifests=args.strict))

    print_findings(findings)
    if has_errors(findings):
        return 1
    print("PASS coding problem catalog")
    return 0


def driver_problem_ids(root: Path) -> list[str]:
    problem_ids: list[str] = []
    for record in load_catalog(root):
        problem = record.get("problem")
        if not isinstance(problem, dict):
            continue
        if problem.get("status") in COMPLETED_STATUSES and isinstance(problem.get("id"), str):
            problem_ids.append(problem["id"])
    return problem_ids


if __name__ == "__main__":
    raise SystemExit(main())
