#!/usr/bin/env python3
"""Validate design-pattern completion matrix against repository structure."""

from __future__ import annotations

import argparse
import re
import sys
import json
import os
import shutil; pass
import subprocess
import tempfile
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


PATTERNS_DIR = Path("01-design-patterns")
MATRIX_FILE = PATTERNS_DIR / "COMPLETION-MATRIX.md"
CATEGORIES = ("creational", "structural", "behavioral")
ROW_RE = re.compile(r"^\|\s*\[(?P<name>[^\]]+)\]\(\./(?P<category>[^/]+)/(?P<slug>[^/]+)/\)\s*\|")


@dataclass(frozen=True)
class Coverage:
    category: str
    slug: str
    theory: str
    java_v1: str
    python_v1: str
    java_tests: str
    python_tests: str
    v2_v3: str


@dataclass(frozen=True)
class Finding:
    kind: str
    path: str
    message: str


def category_label(slug: str) -> str:
    return slug.replace("-", " ").title()


def has_files(directory: Path, pattern: str) -> bool:
    return directory.is_dir() and any(path.is_file() for path in directory.glob(pattern))


def yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def progression_status(pattern_dir: Path) -> str:
    version_dirs = [
        (pattern_dir / "java", "v2-*", "*.java"),
        (pattern_dir / "java", "v3-*", "*.java"),
        (pattern_dir / "python", "v2-*", "*.py"),
        (pattern_dir / "python", "v3-*", "*.py"),
    ]
    present = 0
    for language_dir, version_glob, source_glob in version_dirs:
        if any(has_files(directory, source_glob) for directory in language_dir.glob(version_glob) if directory.is_dir()):
            present += 1
    if present == len(version_dirs):
        return "Yes"
    if present:
        return "Partial"
    return "Planned"


def discover_coverage(root: Path) -> dict[tuple[str, str], Coverage]:
    coverage: dict[tuple[str, str], Coverage] = {}
    for category in CATEGORIES:
        category_dir = root / PATTERNS_DIR / category
        if not category_dir.is_dir() or category_dir.is_symlink():
            continue
        for pattern_dir in sorted(path for path in category_dir.iterdir() if path.is_dir() and not path.is_symlink()):
            key = (category, pattern_dir.name)
            coverage[key] = Coverage(
                category=category_label(category),
                slug=pattern_dir.name,
                theory=yes_no((pattern_dir / "README.md").is_file()),
                java_v1=yes_no(has_files(pattern_dir / "java" / "v1-basic", "*.java")),
                python_v1=yes_no(has_files(pattern_dir / "python" / "v1-basic", "*.py")),
                java_tests=yes_no(has_files(pattern_dir / "java" / "tests", "*.java")),
                python_tests=yes_no(has_files(pattern_dir / "python" / "tests", "*.py")),
                v2_v3=progression_status(pattern_dir),
            )
    return coverage


def parse_matrix(root: Path) -> tuple[dict[tuple[str, str], Coverage], list[Finding]]:
    matrix_path = root / MATRIX_FILE
    findings: list[Finding] = []
    rows: dict[tuple[str, str], Coverage] = {}
    if not matrix_path.is_file() or matrix_path.is_symlink():
        return rows, [Finding("missing-matrix", str(MATRIX_FILE), "completion matrix is required")]

    for line_number, line in enumerate(matrix_path.read_text(encoding="utf-8").splitlines(), start=1):
        match = ROW_RE.match(line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8:
            findings.append(
                Finding(
                    "malformed-matrix-row",
                    f"{MATRIX_FILE}:{line_number}",
                    "pattern matrix row must have 8 columns",
                )
            )
            continue
        category = match.group("category")
        slug = match.group("slug")
        key = (category, slug)
        if key in rows:
            findings.append(
                Finding(
                    "duplicate-matrix-row",
                    f"{MATRIX_FILE}:{line_number}",
                    f"duplicate row for {category}/{slug}",
                )
            )
            continue
        rows[key] = Coverage(
            category=cells[1],
            slug=slug,
            theory=cells[2],
            java_v1=cells[3],
            python_v1=cells[4],
            java_tests=cells[5],
            python_tests=cells[6],
            v2_v3=cells[7],
        )
    return rows, findings


def compare_coverage(root: Path) -> tuple[list[Finding], int]:
    expected = discover_coverage(root)
    actual, findings = parse_matrix(root)

    for key, expected_row in expected.items():
        actual_row = actual.get(key)
        path = str(PATTERNS_DIR / key[0] / key[1])
        if actual_row is None:
            findings.append(
                Finding("missing-matrix-row", path, "pattern folder is not represented in completion matrix")
            )
            continue
        for field in ("category", "theory", "java_v1", "python_v1", "java_tests", "python_tests", "v2_v3"):
            expected_value = getattr(expected_row, field)
            actual_value = getattr(actual_row, field)
            if actual_value != expected_value:
                findings.append(
                    Finding(
                        "stale-matrix-cell",
                        path,
                        f"{field} is {actual_value!r}, expected {expected_value!r}",
                    )
                )

    for key in actual:
        if key not in expected:
            findings.append(
                Finding(
                    "extra-matrix-row",
                    str(MATRIX_FILE),
                    f"matrix row has no matching pattern folder: {key[0]}/{key[1]}",
                )
            )

    return findings, len(expected)



def run_evidence_mode(root: Path, mode: str, junit_jar: str) -> int:
    evidence = discover_evidence_targets(root)
    for target in evidence:
        if not target["has_files"]:
            print(f"pattern-evidence: {target['path']}: failed (missing version)")
            continue
            
        if mode == "plan":
            print(f"pattern-evidence: {target['path']}: structural-presence/not-run")
            continue
            
        # Report mode
        if target["lang"] == "java":
            status = run_java_evidence(root, target, junit_jar)
        else:
            status = run_python_evidence(root, target)
        print(f"pattern-evidence: {target['path']}: {status}")
    return 0

def discover_evidence_targets(root: Path) -> list[dict]:
    targets = []
    for category in CATEGORIES:
        category_dir = root / PATTERNS_DIR / category
        if not category_dir.is_dir() or category_dir.is_symlink():
            continue
        for pattern_dir in sorted(path for path in category_dir.iterdir() if path.is_dir() and not path.is_symlink()):
            for lang in ("java", "python"):
                lang_dir = pattern_dir / lang
                if not lang_dir.is_dir():
                    continue
                # Discover v1-basic, v2-variant, v3-advanced etc.
                for version_dir in sorted(path for path in lang_dir.iterdir() if path.is_dir() and path.name.startswith("v")):
                    ext = "*.java" if lang == "java" else "*.py"
                    has_src = has_files(version_dir, ext)
                    targets.append({
                        "category": category,
                        "pattern": pattern_dir.name,
                        "lang": lang,
                        "version": version_dir.name,
                        "path": f"{category}/{pattern_dir.name}/{lang}/{version_dir.name}",
                        "version_dir": version_dir,
                        "tests_dir": lang_dir / "tests",
                        "has_files": has_src
                    })
    return targets

def run_java_evidence(root: Path, target: dict, junit_jar: str) -> str:
    jar_path = Path(junit_jar)
    if not jar_path.is_file():
        jar_path = root / junit_jar
        if not jar_path.is_file():
            return "blocked (missing junit jar)"
            
    if not target["tests_dir"].is_dir() or not has_files(target["tests_dir"], "*.java"):
        return "failed (missing tests)"
        
    temp_dir = Path(tempfile.mkdtemp(prefix="java_checker_"))
    try:
        # copy sources and tests
        for f in target["version_dir"].rglob("*.java"):
            shutil.copy(f, temp_dir)
        for f in target["tests_dir"].rglob("*.java"):
            shutil.copy(f, temp_dir)
            
        java_files = list(temp_dir.glob("*.java"))
        out_dir = temp_dir / "out"
        out_dir.mkdir()
        
        compile_cmd = ["javac", "--release", "11", "-d", str(out_dir), "-cp", str(jar_path)] + [str(f) for f in java_files]
        comp_res = subprocess.run(compile_cmd, capture_output=True, text=True)
        if comp_res.returncode != 0:
            return "failed (compile error)"
            
        test_cmd = ["java", "-jar", str(jar_path), "execute", "--class-path", str(out_dir), "--details=summary", "--scan-class-path"]
        test_res = subprocess.run(test_cmd, capture_output=True, text=True)
        
        if test_res.returncode != 0:
            return "failed (test execution error)"
            
        tests_successful = 0
        tests_found = 0
        tests_skipped = 0
        for line in test_res.stdout.splitlines():
            line = line.strip()
            if "tests found" in line:
                m = re.search(r'\[\s*(\d+)\s+tests found', line)
                if m: tests_found = int(m.group(1))
            elif "tests skipped" in line:
                m = re.search(r'\[\s*(\d+)\s+tests skipped', line)
                if m: tests_skipped = int(m.group(1))
            elif "tests successful" in line:
                m = re.search(r'\[\s*(\d+)\s+tests successful', line)
                if m: tests_successful = int(m.group(1))
                
        if tests_found == 0:
            return "failed (empty test suite)"
        if tests_skipped > 0:
            return "failed (tests skipped)"
            
        return f"passed with command/test count {tests_successful}"
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def run_python_evidence(root: Path, target: dict) -> str:
    if not target["tests_dir"].is_dir() or not has_files(target["tests_dir"], "*.py"):
        return "failed (missing tests)"
        
    temp_dir = Path(tempfile.mkdtemp(prefix="python_checker_"))
    try:
        # Check for wrong-version provenance (detecting older versions)
        current_version_match = re.search(r'v([0-9]+)', target["version_dir"].name)
        current_version = int(current_version_match.group(1)) if current_version_match else 1
        
        test_files = list(target["tests_dir"].rglob("*.py"))
        for test_file in test_files:
            test_content = test_file.read_text(encoding='utf-8')
            for v in range(1, current_version):
                if f"v{v}" in test_content:
                    return "failed (wrong-version test provenance)"
        
        # Copy sources and tests
        for src_dir in (target["version_dir"], target["tests_dir"]):
            for item in src_dir.rglob("*.py"):
                rel = item.relative_to(src_dir)
                dest = temp_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                if item in test_files:
                    # strip sys.path.insert modifications for isolation
                    content = item.read_text(encoding='utf-8')
                    file_lines = content.split('\n')
                    filtered_lines = [line for line in file_lines if "sys.path.insert" not in line]
                    dest.write_text('\n'.join(filtered_lines), encoding='utf-8')
                else:
                    shutil.copy(item, dest)
                    
        copied_tests = [temp_dir / f.relative_to(target["tests_dir"]) for f in test_files]
            
        runner_script = """
import unittest
import sys
import json
import os

if __name__ == '__main__':
    target_dir = sys.argv[1]
    test_files = sys.argv[2:]
    
    if target_dir not in sys.path:
        sys.path.insert(0, target_dir)
        
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    for test_file in test_files:
        rel_path = os.path.relpath(test_file, target_dir)
        module_name = rel_path.replace('.py', '').replace(os.sep, '.')
        try:
            loaded = loader.loadTestsFromName(module_name)
            suite.addTests(loaded)
        except Exception as e:
            print(json.dumps({"error": f"Failed to load {module_name}: {str(e)}"}))
            sys.exit(1)
            
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    result = runner.run(suite)
    
    results = {
        "testsRun": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped)
    }
    
    print(json.dumps(results))
    sys.exit(0 if result.wasSuccessful() else 1)
"""
        runner_path = temp_dir / "runner.py"
        runner_path.write_text(runner_script, encoding='utf-8')
        
        env = os.environ.copy()
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        
        cmd = [sys.executable, "-B", str(runner_path), str(temp_dir)] + [str(p) for p in copied_tests]
        
        res = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        try:
            out_lines = res.stdout.strip().split('\n')
            result_data = json.loads(out_lines[-1])
        except (json.JSONDecodeError, IndexError):
            return f"failed (runner error: {res.stderr.strip()})"
            
        if "error" in result_data:
            return f"failed ({result_data['error']})"
            
        testsRun = result_data.get("testsRun", 0)
        failures = result_data.get("failures", 0)
        errors = result_data.get("errors", 0)
        skipped = result_data.get("skipped", 0)
        
        if testsRun == 0:
            return "failed (empty test suite)"
        if skipped > 0:
            return f"failed (tests skipped)"
        if failures > 0 or errors > 0:
            return f"failed (test execution error)"
            
        return f"passed with command/test count {testsRun}"
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    parser.add_argument("--evidence-plan", action="store_true", help="Print evidence plan for all pattern versions.")
    parser.add_argument("--evidence-report", action="store_true", help="Run tests and print evidence report for all pattern versions.")
    parser.add_argument("--junit-jar", default="junit-platform-console-standalone.jar", help="JUnit platform console standalone jar path.")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()

    if args.evidence_plan or args.evidence_report:
        return run_evidence_mode(root, "plan" if args.evidence_plan else "report", args.junit_jar)

    findings, total = compare_coverage(root)

    print(f"summary: patterns={total}")
    if findings:
        for finding in findings:
            print(f"{finding.kind}: {finding.path}: {finding.message}")
        return 1

    print("pattern-completion: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
