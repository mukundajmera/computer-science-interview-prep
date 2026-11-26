#!/usr/bin/env python3
"""Preflight and run a narrow Java smoke compile without source-tree outputs."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


MIN_JAVA_MAJOR = 11
DEFAULT_COMPILE_TARGET = "02-lld-projects/parking-lot/java/v1-basic"
DEFAULT_OUTPUT_DIR = "/tmp/sdip-java-smoke"
DEFAULT_JUNIT_JAR = "junit-platform-console-standalone.jar"


@dataclass(frozen=True)
class ToolResult:
    returncode: int
    output: str


def run_tool(command: Sequence[str], root: Path) -> ToolResult:
    result = subprocess.run(
        command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return ToolResult(result.returncode, result.stdout.strip())


def parse_java_major(output: str) -> tuple[int, str] | None:
    match = re.search(r'version "([^"]+)"', output)
    if not match:
        match = re.search(r"\b(?:java|javac)\s+([0-9][^\s]*)", output)
    if not match:
        return None
    version = match.group(1)
    parts = version.split(".")
    if len(parts) > 1 and parts[0] == "1":
        return int(parts[1]), version
    return int(parts[0]), version


def resolve_repo_path(root: Path, path_text: str, label: str) -> Path:
    candidate = Path(path_text)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"{label} must be inside repository: {path_text}")
    return resolved


def resolve_output_dir(root: Path, path_text: str) -> Path:
    resolved = Path(path_text).expanduser().resolve()
    if resolved == root or root in resolved.parents:
        raise ValueError("output directory must be outside repository")
    return resolved


def resolve_junit_jar(root: Path, path_text: str | None) -> Path:
    selected = path_text or os.environ.get("JUNIT_PLATFORM_CONSOLE_STANDALONE_JAR") or DEFAULT_JUNIT_JAR
    candidate = Path(selected).expanduser()
    return (candidate if candidate.is_absolute() else root / candidate).resolve()


def check_java(root: Path) -> bool:
    if shutil.which("java") is None:
        print("BLOCKED java: required tool not found: java")
        return False
    result = run_tool(["java", "-version"], root)
    if result.returncode != 0:
        if result.output:
            print(result.output)
        print("BLOCKED java: required tool not usable: java")
        return False
    parsed = parse_java_major(result.output)
    if parsed is None:
        print("BLOCKED java_version: unable to parse java -version output")
        return False
    major, version = parsed
    if major < MIN_JAVA_MAJOR:
        print(f"BLOCKED java_version: Java {MIN_JAVA_MAJOR}+ required, found {version}")
        return False
    print(f"PASS java_version: {version}")
    return True


def check_javac(root: Path) -> bool:
    if shutil.which("javac") is None:
        print("BLOCKED javac: required tool not found: javac")
        return False
    result = run_tool(["javac", "-version"], root)
    if result.returncode != 0:
        if result.output:
            print(result.output)
        print("BLOCKED javac: required tool not usable: javac")
        return False
    parsed = parse_java_major(result.output)
    version = parsed[1] if parsed else result.output
    print(f"PASS javac: {version}")
    return True


def check_junit(junit_jar: Path) -> bool:
    if not junit_jar.is_file():
        print(f"BLOCKED junit: missing JUnit console jar: {junit_jar}")
        return False
    print(f"PASS junit: {junit_jar}")
    return True


def java_files(source_dir: Path) -> list[Path]:
    return sorted(path for path in source_dir.glob("*.java") if path.is_file())


def compile_sources(root: Path, source_dir: Path, output_dir: Path) -> bool:
    sources = java_files(source_dir)
    if not sources:
        print(f"FAIL compile: no Java source files in {source_dir}")
        return False
    output_dir.mkdir(parents=True, exist_ok=True)
    command = ["javac", "-d", str(output_dir), *(str(source) for source in sources)]
    result = run_tool(command, root)
    if result.returncode != 0:
        if result.output:
            print(result.output)
        print(f"FAIL compile: exit {result.returncode}")
        return False
    print(f"PASS compile: {source_dir} -> {output_dir}")
    return True


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--preflight-only", action="store_true", help="Check Java/Javac/JUnit availability only.")
    parser.add_argument("--compile-target", default=DEFAULT_COMPILE_TARGET, help="Repository-local Java source directory.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Compile output directory outside the repository.")
    parser.add_argument("--junit-jar", help="JUnit platform console standalone jar path. Defaults to env or repo root jar.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.root).resolve()
    try:
        compile_target = resolve_repo_path(root, args.compile_target, "compile target")
        output_dir = resolve_output_dir(root, args.output_dir)
        junit_jar = resolve_junit_jar(root, args.junit_jar)
    except ValueError as error:
        print(f"java-smoke: error: {error}", file=sys.stderr)
        return 1

    checks_ok = True
    checks_ok = check_java(root) and checks_ok
    checks_ok = check_javac(root) and checks_ok
    checks_ok = check_junit(junit_jar) and checks_ok
    if args.preflight_only or not checks_ok:
        return 0 if checks_ok else 1
    return 0 if compile_sources(root, compile_target, output_dir) else 1


if __name__ == "__main__":
    raise SystemExit(main())
