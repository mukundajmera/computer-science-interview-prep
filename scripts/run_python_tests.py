#!/usr/bin/env python3
"""Run each Python tests folder in isolation.

Running pytest once over several project folders fails with module-name
collisions because many projects use a package literally called ``tests``.
This runner instead discovers every tracked ``test_*.py`` file, groups them
into per-project test units, and runs each unit in its own subprocess.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Sequence

TESTS_DIR_NAME = "tests"


def tracked_test_files(root: Path) -> List[str]:
    result = subprocess.run(
        ["git", "ls-files", "test_*.py", "**/test_*.py"],
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )
    return sorted(name for name in result.stdout.splitlines() if name)


def unit_for(test_file: str) -> str:
    parts = Path(test_file).parts
    for index, part in enumerate(parts[:-1]):
        if part == TESTS_DIR_NAME:
            return str(Path(*parts[: index + 1]))
    return str(Path(*parts[:-1]))


def test_units(root: Path) -> List[str]:
    units = {unit_for(name) for name in tracked_test_files(root)}
    return sorted(units)


def pytest_available() -> bool:
    return importlib.util.find_spec("pytest") is not None


def run_unit(root: Path, unit: str, timeout: int) -> bool:
    if pytest_available():
        command = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", unit, "-q"]
    else:
        command = [sys.executable, "-m", "unittest", "discover", unit]
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        result = subprocess.run(
            command,
            cwd=str(root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False
    return result.returncode == 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--list", action="store_true", help="print the test folders and run nothing")
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="SUBSTRING",
        help="run only folders containing this substring (repeatable)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="per-folder timeout in seconds (default: 120); a timeout counts as FAIL",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    units = test_units(root)
    if args.only:
        units = [unit for unit in units if any(token in unit for token in args.only)]

    if args.list:
        for unit in units:
            print(unit)
        return 0

    failures = 0
    for unit in units:
        passed = run_unit(root, unit, args.timeout)
        print(("PASS " if passed else "FAIL ") + unit)
        failures += 0 if passed else 1

    print(f"python-test-runner: {len(units) - failures} passed, {failures} failed, {len(units)} folders")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
