#!/usr/bin/env python3
"""Run named repository validation smoke checks."""

from __future__ import annotations

import argparse
import os
import shutil
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class Check:
    name: str
    command: tuple[str, ...]
    description: str
    required_tool: str | None = None
    default: bool = True
    blocked_patterns: tuple[str, ...] = ()
    unsafe_driver_execution: bool = False


CHECKS = [
    Check(
        "check_scripts",
        ("python3", "-B", "-m", "unittest", "discover", "scripts/tests", "-v"),
        "Run local validation script unit tests.",
        required_tool="python3",
    ),
    Check(
        "check_portal",
        ("npm", "--prefix", "apps/portal", "run", "lint"),
        "Run portal lint. Use npm run build separately for full portal build evidence.",
        required_tool="npm",
    ),
    Check(
        "check_python_smoke",
        (
            "python3",
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            "02-lld-projects/tic-tac-toe/python/tests",
            "-q",
        ),
        "Run a narrow Python project smoke test.",
        required_tool="python3",
    ),
    Check(
        "check_python_failing",
        (
            "python3",
            "-m",
            "pytest",
            "-p",
            "no:cacheprovider",
            "06-genai-systems/01-llm-lld-projects/embedding-service/python/tests",
            "-q",
        ),
        "Run the non-default GenAI Python regression gate tracked as known debt.",
        required_tool="python3",
        default=False,
    ),
    Check(
        "check_java_smoke",
        ("python3", "scripts/check_java_smoke.py"),
        "Verify Java 11+, javac, JUnit jar, and a /tmp Java compile smoke when available.",
        required_tool="python3",
        default=False,
        blocked_patterns=("BLOCKED ",),
    ),
    Check(
        "check_markdown_links",
        (
            "python3",
            "scripts/check_markdown_links.py",
            "README.md",
            "QUICK-START.md",
            "CONCEPTS.md",
            "resources/README.md",
            "resources/CONTENT-UI-MAP.md",
            "quizzes/README.md",
            "apps/portal/AGENTS.md",
            "03-hld-concepts/README.md",
        ),
        "Run known-healthy local Markdown link sample.",
        required_tool="python3",
    ),
    Check(
        "check_content_inventory",
        ("python3", "scripts/check_content_inventory.py", "--sections", "case-studies", "coding"),
        "Run known-healthy content inventory sections.",
        required_tool="python3",
    ),
    Check(
        "check_coding_problem_catalog",
        ("python3", "-B", "scripts/check_coding_problem_catalog.py"),
        "Validate coding problem bank schema, source manifests, and path contracts.",
        required_tool="python3",
    ),
    Check(
        "check_coding_problem_driver_generation",
        ("python3", "-B", "scripts/check_coding_problem_catalog.py", "--driver-generation"),
        "Validate generated coding problem driver source without executing solution code.",
        required_tool="python3",
    ),
    Check(
        "check_coding_problem_python_drivers",
        (
            "python3",
            "-B",
            "scripts/check_coding_problem_catalog.py",
            "--drivers",
            "--allow-unsafe-driver-execution",
            "--language",
            "python",
        ),
        "Run generated Python drivers for solution-bearing coding problems.",
        required_tool="python3",
        default=False,
        unsafe_driver_execution=True,
    ),
    Check(
        "check_coding_problem_artifacts",
        (
            "python3",
            "-B",
            "scripts/check_coding_problem_artifacts.py",
        ),
        "Verify coding problem bank paths do not contain ignored driver/cache artifacts.",
        required_tool="python3",
    ),
    Check(
        "check_coding_problem_java_drivers",
        (
            "python3",
            "-B",
            "scripts/check_coding_problem_catalog.py",
            "--drivers",
            "--allow-unsafe-driver-execution",
            "--language",
            "java",
        ),
        "Run generated Java drivers for solution-bearing coding problems when a real JDK is available.",
        required_tool="python3",
        default=False,
        blocked_patterns=("Java toolchain is not available", "Java toolchain must be Java 11+"),
        unsafe_driver_execution=True,
    ),
    Check(
        "check_readability_style",
        ("python3", "scripts/check_readability_style.py"),
        "Validate scoped learner-facing Markdown for placeholders and generic outline prose.",
        required_tool="python3",
    ),
    Check(
        "check_hld_concept_catalog",
        ("python3", "scripts/check_hld_concept_catalog.py"),
        "Validate HLD concept README catalog, mapping, and checklist coverage.",
        required_tool="python3",
    ),
    Check(
        "check_genai_currentness",
        ("python3", "scripts/check_genai_currentness.py"),
        "Validate GenAI currentness ledger and GenAI HLD interview solution parity.",
        required_tool="python3",
    ),
    Check(
        "check_assessment_coverage",
        ("python3", "-B", "scripts/check_assessment_coverage.py"),
        "Validate quiz, flashcard, and interview solution assessment coverage matrix.",
        required_tool="python3",
    ),
    Check(
        "check_pattern_completion",
        ("python3", "scripts/check_pattern_completion.py"),
        "Validate design-pattern completion matrix against actual folders.",
        required_tool="python3",
    ),
    Check(
        "check_lld_project_coverage",
        ("python3", "scripts/check_lld_project_coverage.py"),
        "Validate LLD project coverage matrix against actual folders.",
        required_tool="python3",
    ),
    Check(
        "check_executable_sample_inventory",
        ("python3", "scripts/check_executable_sample_inventory.py"),
        "Validate executable sample inventory against concept source files.",
        required_tool="python3",
    ),
    Check(
        "check_secret_artifacts",
        ("python3", "scripts/check_tracked_secret_artifacts.py"),
        "Scan tracked paths for credential-like local artifact names.",
        required_tool="python3",
    ),
    Check(
        "check_checkpoint_boundary",
        ("python3", "scripts/check_checkpoint_boundary.py"),
        "Validate that the git worktree has a coherent staged checkpoint boundary.",
        required_tool="python3",
        default=False,
    ),
    Check(
        "check_mermaid",
        ("mmdc", "--version"),
        "Verify Mermaid CLI availability before diagram rendering.",
        required_tool="mmdc",
        default=False,
    ),
]
CHECK_BY_NAME = {check.name: check for check in CHECKS}
BOUNDARY_PROFILE_CHECKS = ("check_checkpoint_boundary",)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run repository validation smoke checks.")
    parser.add_argument("--list", action="store_true", help="List available named checks.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them.")
    parser.add_argument(
        "--profile",
        choices=("default", "checkpoint", "release"),
        default="default",
        help="Check profile to run when --only is not supplied. checkpoint/release add boundary checks.",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        help="Run only the named checks. Defaults to non-optional smoke checks.",
    )
    parser.add_argument(
        "--allow-unsafe-driver-execution",
        action="store_true",
        help="Allow smoke checks that execute coding problem solution code.",
    )
    return parser.parse_args(argv)


def selected_checks(names: Sequence[str] | None, profile: str = "default") -> list[Check]:
    if not names:
        checks = [check for check in CHECKS if check.default]
        if profile in {"checkpoint", "release"}:
            checks.extend(CHECK_BY_NAME[name] for name in BOUNDARY_PROFILE_CHECKS)
        return checks
    checks = []
    for name in names:
        check = CHECK_BY_NAME.get(name)
        if check is None:
            raise ValueError(f"unknown check: {name}")
        checks.append(check)
    return checks


def command_text(command: Sequence[str]) -> str:
    return shlex.join(command)


def run_check(check: Check, root: Path, dry_run: bool, allow_unsafe_driver_execution: bool) -> int:
    if dry_run:
        print(f"DRY-RUN {check.name}: {command_text(check.command)}")
        return 0
    if check.unsafe_driver_execution and not allow_unsafe_driver_execution:
        print(
            f"BLOCKED {check.name}: requires --allow-unsafe-driver-execution "
            "because this check executes solution code"
        )
        return 1
    if check.required_tool and shutil.which(check.required_tool) is None:
        print(f"BLOCKED {check.name}: required tool not found: {check.required_tool}")
        return 1
    env = os.environ.copy()
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    result = subprocess.run(
        check.command,
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.returncode == 0:
        print(f"PASS {check.name}")
        return 0
    if any(pattern in result.stdout for pattern in check.blocked_patterns):
        print(f"BLOCKED {check.name}: preflight blocker")
        return 1
    print(f"FAIL {check.name}: exit {result.returncode}")
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.list:
        for check in CHECKS:
            optional = " optional" if not check.default else ""
            print(f"{check.name}{optional}: {check.description}")
        return 0

    try:
        checks = selected_checks(args.only, args.profile)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parents[1]
    failures = 0
    for check in checks:
        failures += run_check(check, root, args.dry_run, args.allow_unsafe_driver_execution)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
