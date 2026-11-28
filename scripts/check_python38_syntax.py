#!/usr/bin/env python3
"""Guard that every tracked Python file still parses as Python 3.8 syntax."""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path
from typing import Sequence


def git_ls_python_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "*.py"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "unknown error"
        raise RuntimeError(f"git ls-files failed: {detail}")
    return sorted(path for path in result.stdout.splitlines() if path)


def check_file(root: Path, relative: str) -> str | None:
    path = root / relative
    if not path.is_file():
        return None
    source = path.read_text(encoding="utf-8")
    try:
        ast.parse(source, filename=relative, feature_version=(3, 8))
    except SyntaxError as exc:
        line = exc.lineno or 0
        message = exc.msg or "syntax error"
        return f"{relative}:{line}: {message}"
    return None


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parse every tracked .py file with Python 3.8 grammar."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Directory used as the cwd for git ls-files (default: current directory).",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    failures = []
    checked = 0
    for relative in git_ls_python_files(root):
        if not (root / relative).is_file():
            continue
        checked += 1
        failure = check_file(root, relative)
        if failure is not None:
            failures.append(failure)

    for failure in failures:
        print(failure)
    if failures:
        return 1

    print(f"python38-syntax: ok ({checked} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
