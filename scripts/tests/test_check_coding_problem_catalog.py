#!/usr/bin/env python3
"""Tests for the coding problem catalog validator."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.coding_catalog.load import load_catalog, load_source_manifests
from scripts.coding_catalog.schema import (
    BLOCKED_SOURCE_HASHES_ENV,
    BLOCKED_SOURCE_HASH_FILE_ENV,
    blocked_source_example_hash,
    source_metadata_hash,
    validate_catalog,
    validate_source_manifests,
)
from scripts.coding_catalog.driver import (
    java_check_expression,
    java_major_version,
    java_toolchain_error,
    java_driver_source,
    matches,
    run_problem_drivers,
    run_python_solution_subprocess,
    validate_driver_generation,
)
from scripts.coding_catalog.collections import render_collection_pages


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_python_command(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    command_env = os.environ.copy()
    command_env["PYTHONDONTWRITEBYTECODE"] = "1"
    if env:
        command_env.update(env)
    return subprocess.run(
        command,
        cwd=cwd,
        env=command_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


@contextmanager
def blocked_source_hashes(*values: object):
    old_hashes = os.environ.get(BLOCKED_SOURCE_HASHES_ENV)
    old_hash_file = os.environ.get(BLOCKED_SOURCE_HASH_FILE_ENV)
    os.environ[BLOCKED_SOURCE_HASHES_ENV] = ",".join(blocked_source_example_hash(value) for value in values)
    os.environ.pop(BLOCKED_SOURCE_HASH_FILE_ENV, None)
    try:
        yield
    finally:
        if old_hashes is None:
            os.environ.pop(BLOCKED_SOURCE_HASHES_ENV, None)
        else:
            os.environ[BLOCKED_SOURCE_HASHES_ENV] = old_hashes
        if old_hash_file is None:
            os.environ.pop(BLOCKED_SOURCE_HASH_FILE_ENV, None)
        else:
            os.environ[BLOCKED_SOURCE_HASH_FILE_ENV] = old_hash_file


def valid_problem(root: Path, problem_id: str = "lc-0001-two-sum") -> Path:
    problem = root / "05-coding-problems" / "problem-bank" / problem_id
    write_json(
        problem / "problem.json",
        {
            "id": problem_id,
            "title": "Two Sum",
            "difficulty": "easy",
            "status": "verified",
            "patterns": ["array", "hash-map"],
            "provenance": {
                "sourceUse": "metadata-only",
                "problemSummary": "repo-authored-clean-room",
                "examples": "repo-authored-clean-room",
                "cases": "repo-authored-clean-room",
            },
            "cleanRoomReview": {
                "reviewedAt": "2026-06-13",
                "reviewer": "codex",
                "scope": ["problem.json", "README.md", "cases.json", "solutions.json"],
                "verdict": "no-source-statement-or-example-copying-detected",
            },
            "validation": {
                "validatedAt": "2026-06-13",
                "checks": [
                    {
                        "name": "catalog-strict",
                        "status": "passed",
                        "command": "python3 -B scripts/check_coding_problem_catalog.py --strict",
                    },
                    {
                        "name": "driver-generation",
                        "status": "passed",
                        "language": "java",
                        "command": "python3 -B scripts/check_coding_problem_catalog.py --driver-generation",
                    },
                    {
                        "name": "python-drivers",
                        "status": "passed",
                        "language": "python",
                        "command": "python3 -B scripts/check_coding_problem_catalog.py --drivers --allow-unsafe-driver-execution --language python",
                    },
                    {
                        "name": "java-drivers",
                        "status": "blocked",
                        "language": "java",
                        "reason": "missing-jdk-11",
                        "command": "python3 -B scripts/check_repo_smoke.py --only check_coding_problem_java_drivers --allow-unsafe-driver-execution",
                    },
                ],
            },
            "collections": [
                {
                    "id": "leetcode-top-150",
                    "order": 45,
                    "group": "Hashmap",
                    "sourceUrl": "https://leetcode.com/problems/two-sum",
                }
            ],
            "leetcode": {
                "frontendId": "1",
                "titleSlug": "two-sum",
                "url": "https://leetcode.com/problems/two-sum",
                "paidOnly": False,
            },
            "signature": {
                "java": {
                    "className": "Solution",
                    "methodName": "twoSum",
                    "returnType": "int[]",
                    "parameters": [
                        {"name": "nums", "type": "int[]"},
                        {"name": "target", "type": "int"},
                    ],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "twoSum",
                    "returnType": "List[int]",
                    "parameters": [
                        {"name": "nums", "type": "List[int]"},
                        {"name": "target", "type": "int"},
                    ],
                },
            },
        },
    )
    write_json(
        problem / "cases.json",
        {
            "source": "repo-authored-clean-room",
            "matcher": {"type": "exact"},
            "cases": [
                {
                    "name": "repo-authored simple pair",
                    "input": {"nums": [4, 6, 10], "target": 10},
                    "expected": [0, 1],
                }
            ],
        },
    )
    write_text(
        problem / "README.md",
        "\n".join(
            [
                "# Two Sum",
                "",
                "Clean-room summary: find two different positions whose values meet the target sum.",
                "",
            ]
        ),
    )
    write_json(
        problem / "solutions.json",
        {
            "solutions": [
                {
                    "id": "solution-1-brute-force",
                    "title": "Brute force pair scan",
                    "tier": 1,
                    "strategy": "Check every index pair until a valid sum is found.",
                    "timeComplexity": {
                        "class": "O(n^2)",
                        "explanation": "The nested loops compare each index with every later index, which produces a quadratic number of pair checks.",
                    },
                    "spaceComplexity": {
                        "class": "O(1)",
                        "explanation": "The algorithm stores only loop counters and the returned pair, so auxiliary space does not grow with input size.",
                    },
                    "javaPath": "java/solution-1-brute-force/Solution.java",
                    "pythonPath": "python/solution-1-brute-force/solution.py",
                }
            ]
        },
    )
    write_text(problem / "java" / "solution-1-brute-force" / "Solution.java")
    write_text(problem / "python" / "solution-1-brute-force" / "solution.py")
    return problem


def finding_messages(findings):
    return "\n".join(f"{finding.path}: {finding.message}" for finding in findings)


def quad_tree_leaf(value: bool) -> dict[str, object]:
    return {
        "val": value,
        "isLeaf": True,
        "topLeft": None,
        "topRight": None,
        "bottomLeft": None,
        "bottomRight": None,
    }


def quad_tree_node(
    top_left: dict[str, object] | None,
    top_right: dict[str, object] | None,
    bottom_left: dict[str, object] | None,
    bottom_right: dict[str, object] | None,
) -> dict[str, object]:
    return {
        "val": True,
        "isLeaf": False,
        "topLeft": top_left,
        "topRight": top_right,
        "bottomLeft": bottom_left,
        "bottomRight": bottom_right,
    }


def valid_source_manifest(collection_id: str = "leetcode-top-150") -> dict[str, object]:
    source_url = {
        "leetcode-top-150": "https://leetcode.com/studyplan/top-interview-150/",
        "grind-169": "https://www.techinterviewhandbook.org/grind75/",
        "neetcode-all": "https://neetcode.io/practice",
    }[collection_id]
    item = {
        "sourceId": "1",
        "title": "Two Sum",
        "titleSlug": "two-sum",
        "sourceUrl": "https://leetcode.com/problems/two-sum",
        "collectionId": collection_id,
        "group": "Hashmap",
        "order": 1,
        "difficulty": "easy",
        "dedupeKey": "leetcode:1:two-sum",
        "canonicalId": "lc-0001-two-sum",
    }
    items = [item]
    return {
        "collectionId": collection_id,
        "sourceStatus": "pinned",
        "sourceUrl": source_url,
        "snapshotDate": "2026-06-13",
        "expectedCount": 1,
        "provenance": {
            "fetchDate": "2026-06-13",
            "sourcePages": [source_url],
            "fetchMethod": "websearch-and-public-metadata",
            "extractorVersion": "coding-list-intake-v1",
            "metadataSha256": source_metadata_hash(items),
            "reviewReceipt": "metadata-only-clean-room-intake-2026-06-13",
            "rawSourceRetention": "not-retained-copyright-minimization",
        },
        "items": items,
    }


def java_toolchain_available() -> bool:
    return java_toolchain_error() is None


class CatalogValidationTest(unittest.TestCase):
    def test_valid_problem_catalog_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid_problem(root)

            catalog = load_catalog(root)
            findings = validate_catalog(catalog, root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_catalog_loader_ignores_symlinked_problem_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = Path(tmp) / "outside-bank"
            valid_problem(outside)
            bank = root / "05-coding-problems" / "problem-bank"
            bank.mkdir(parents=True)
            (bank / "lc-0001-two-sum").symlink_to(
                outside / "05-coding-problems" / "problem-bank" / "lc-0001-two-sum",
                target_is_directory=True,
            )

            self.assertEqual([], load_catalog(root))

    def test_catalog_loader_reports_invalid_problem_json_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            (problem / "cases.json").write_text("{broken", encoding="utf-8")

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("invalid JSON at line 1 column 2", messages)
            self.assertIn("completed problem must have cases.json", messages)

    def test_duplicate_problem_ids_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid_problem(root, "lc-0001-two-sum")
            other = valid_problem(root, "lc-0001-two-sum-copy")
            payload = json.loads((other / "problem.json").read_text(encoding="utf-8"))
            payload["id"] = "lc-0001-two-sum"
            write_json(other / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("duplicate canonical problem id", finding_messages(findings))

    def test_duplicate_collection_membership_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["collections"].append(dict(payload["collections"][0]))
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("duplicate collection membership", finding_messages(findings))

    def test_completed_problem_requires_one_to_five_solutions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = {"solutions": []}
            write_json(problem / "solutions.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("must have at least one solution", finding_messages(findings))

            payload["solutions"] = [
                {
                    "id": f"solution-{index}-x",
                    "title": "x",
                    "tier": index,
                    "strategy": "x",
                    "timeComplexity": {"class": "O(1)", "explanation": "constant work"},
                    "spaceComplexity": {"class": "O(1)", "explanation": "constant storage"},
                    "javaPath": "java/solution-1-brute-force/Solution.java",
                    "pythonPath": "python/solution-1-brute-force/solution.py",
                }
                for index in range(1, 7)
            ]
            write_json(problem / "solutions.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("must not have more than five solutions", finding_messages(findings))

    def test_completed_problem_requires_java_python_paths_and_complexity_explanations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "solutions.json").read_text(encoding="utf-8"))
            solution = payload["solutions"][0]
            solution.pop("javaPath")
            solution["pythonPath"] = "python/missing/solution.py"
            solution["timeComplexity"]["explanation"] = ""
            solution["spaceComplexity"].pop("explanation")
            write_json(problem / "solutions.json", payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("missing javaPath", messages)
            self.assertIn("pythonPath does not exist", messages)
            self.assertIn("timeComplexity.explanation is required", messages)
            self.assertIn("spaceComplexity.explanation is required", messages)

    def test_solution_tiers_must_be_contiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "solutions.json").read_text(encoding="utf-8"))
            payload["solutions"][0]["tier"] = 2
            write_json(problem / "solutions.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("solution tiers must be contiguous starting at 1", finding_messages(findings))

    def test_problem_status_must_be_known(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["status"] = "verfied"
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("status must be one of", finding_messages(findings))

    def test_solution_paths_must_stay_inside_language_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "solutions.json").read_text(encoding="utf-8"))
            payload["solutions"][0]["javaPath"] = "/tmp/Solution.java"
            payload["solutions"][0]["pythonPath"] = "../outside.py"
            write_json(problem / "solutions.json", payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("javaPath must be relative", messages)
            self.assertIn("pythonPath must live under python/", messages)

    def test_completed_problem_requires_clean_room_provenance_and_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload.pop("provenance")
            problem_payload.pop("cleanRoomReview")
            write_json(problem / "problem.json", problem_payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload.pop("source")
            cases_payload["cases"] = []
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("completed problem must define provenance", messages)
            self.assertIn("completed problem must define cleanRoomReview", messages)
            self.assertIn("cases source must be repo-authored-clean-room", messages)
            self.assertIn("completed problem must define at least one test case", messages)

    def test_completed_problem_requires_validation_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload.pop("validation")
            write_json(problem / "problem.json", problem_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("completed problem must define validation receipt", finding_messages(findings))

            problem_payload["validation"] = {
                "validatedAt": "2026-06-13",
                "checks": [
                    {
                        "name": "catalog-strict",
                        "status": "blocked",
                        "command": "python3 -B scripts/check_coding_problem_catalog.py --strict",
                    },
                    {
                        "name": "java-drivers",
                        "status": "blocked",
                        "language": "java",
                        "reason": "certificate-expired",
                        "command": "python3 -B scripts/check_repo_smoke.py --only check_coding_problem_java_drivers --allow-unsafe-driver-execution",
                    },
                ],
            }
            write_json(problem / "problem.json", problem_payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("validation check catalog-strict must be passed", messages)
            self.assertIn("missing validation check driver-generation", messages)
            self.assertIn("missing validation check python-drivers", messages)
            self.assertIn("blocked java-drivers validation check must use reason missing-jdk-11", messages)

    def test_validation_receipt_checks_exact_command_and_language_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            checks = problem_payload["validation"]["checks"]
            checks[0]["command"] = "echo ok"
            checks[0]["language"] = "python"
            checks[1].pop("language")
            checks[2]["language"] = "java"
            checks.append(
                {
                    "name": "portal-lint",
                    "status": "passed",
                    "command": "npm --prefix apps/portal run lint",
                }
            )
            write_json(problem / "problem.json", problem_payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn(
                "validation check catalog-strict command must be python3 -B scripts/check_coding_problem_catalog.py --strict",
                messages,
            )
            self.assertIn("validation check catalog-strict must not define language", messages)
            self.assertIn("validation check driver-generation language must be java", messages)
            self.assertIn("validation check python-drivers language must be python", messages)
            self.assertIn("unexpected validation check portal-lint", messages)

    def test_balanced_bst_matcher_requires_tree_node_sorted_array_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "balanced-bst-from-sorted-array"}
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "balanced-bst-from-sorted-array matcher requires a TreeNode return signature",
                finding_messages(findings),
            )

    def test_unordered_tree_list_matcher_requires_tree_node_list_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "unordered-tree-list"}
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "unordered-tree-list matcher requires a List<TreeNode> return signature",
                finding_messages(findings),
            )

    def test_signature_types_allow_unordered_tree_node_list_returns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "generateTrees",
                "returnType": "List<TreeNode>",
                "parameters": [{"name": "n", "type": "int"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "generateTrees",
                "returnType": "List[Optional[TreeNode]]",
                "parameters": [{"name": "n", "type": "int"}],
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "unordered-tree-list"},
                    "cases": [
                        {
                            "name": "two possible roots",
                            "input": {"n": 2},
                            "expected": [[1, None, 2], [2, 1]],
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_unordered_list_matcher_requires_supported_nested_list_return_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "unordered-list-of-lists"}
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "unordered-list-of-lists matcher requires a nested list return signature",
                finding_messages(findings),
            )

    def test_unordered_list_matchers_validate_expected_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"]["returnType"] = "List<List<Integer>>"
            problem_payload["signature"]["python"]["returnType"] = "List[List[int]]"
            write_json(problem / "problem.json", problem_payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "unordered-list-of-lists"}
            cases_payload["cases"][0]["expected"] = [[1, "2"]]
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "case 1 expected must be a list of lists matching unordered-list-of-lists return type",
                finding_messages(findings),
            )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"]["returnType"] = "List<String>"
            problem_payload["signature"]["python"]["returnType"] = "List[str]"
            write_json(problem / "problem.json", problem_payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "unordered-list"}
            cases_payload["cases"][0]["expected"] = ["ok", 3]
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "case 1 expected must be a flat list matching unordered-list return type",
                finding_messages(findings),
            )

    def test_valid_topological_order_matcher_requires_course_schedule_ii_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "valid-topological-order"}
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "valid-topological-order matcher requires Course Schedule II signatures",
                finding_messages(findings),
            )

    def test_valid_topological_order_matcher_validates_input_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "findOrder",
                "returnType": "int[]",
                "parameters": [
                    {"name": "numCourses", "type": "int"},
                    {"name": "prerequisites", "type": "int[][]"},
                ],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "findOrder",
                "returnType": "List[int]",
                "parameters": [
                    {"name": "numCourses", "type": "int"},
                    {"name": "prerequisites", "type": "List[List[int]]"},
                ],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "valid-topological-order"},
                    "cases": [
                        {
                            "name": "malformed edge",
                            "input": {"numCourses": 3, "prerequisites": [[1, 0, 2], [4, 0]]},
                            "expected": [],
                        },
                        {
                            "name": "bad course count",
                            "input": {"numCourses": -1, "prerequisites": []},
                            "expected": [],
                        },
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("case 1 input.prerequisites[1] must be a two-integer edge", messages)
            self.assertIn("case 1 input.prerequisites[2] contains an out-of-range course", messages)
            self.assertIn("case 2 input.numCourses must be a non-negative integer", messages)

    def test_clean_room_review_scope_files_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            (problem / "README.md").unlink()

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "cleanRoomReview.scope includes missing reviewed file README.md",
                finding_messages(findings),
            )

    def test_clean_room_review_scans_solution_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            blocked_line = "private blocked source transcript alpha 314159"
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def twoSum(self, nums, target):\n"
                f"        # {blocked_line}\n"
                "        return []\n",
            )

            with blocked_source_hashes(blocked_line):
                findings = validate_catalog(load_catalog(root), root)

            self.assertIn("content appears to reuse a blocked source example", finding_messages(findings))

    def test_python_solution_source_requires_python38_compatible_annotations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def twoSum(self, nums: list[int], target: int) -> list[int]:\n"
                "        return []\n",
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "pythonPath uses Python 3.9 built-in generics without postponed annotations",
                finding_messages(findings),
            )

    def test_python_solution_source_allows_postponed_builtin_generics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from __future__ import annotations\n\n"
                "class Solution:\n"
                "    def twoSum(self, nums: list[int], target: int) -> list[int]:\n"
                "        return []\n",
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn(
                "pythonPath uses Python 3.9 built-in generics without postponed annotations",
                finding_messages(findings),
            )

    def test_python_solution_source_rejects_commented_future_import_bypass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "# from __future__ import annotations\n"
                "class Solution:\n"
                "    def twoSum(self, nums: list[int], target: int) -> list[int]:\n"
                "        return []\n",
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "pythonPath uses Python 3.9 built-in generics without postponed annotations",
                finding_messages(findings),
            )

    def test_python_solution_source_rejects_late_future_import_bypass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "VALUE = 1\n"
                "from __future__ import annotations\n\n"
                "class Solution:\n"
                "    def twoSum(self, nums: list[int], target: int) -> list[int]:\n"
                "        return []\n",
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "pythonPath uses Python 3.9 built-in generics without postponed annotations",
                finding_messages(findings),
            )

    def test_clean_room_review_rejects_solution_source_symlink_before_reading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            outside = root / "outside-solution.py"
            blocked_line = "private blocked source transcript beta 271828"
            write_text(outside, f"# {blocked_line}\n")
            solution = problem / "python" / "solution-1-brute-force" / "solution.py"
            solution.unlink()
            solution.symlink_to(outside)

            with blocked_source_hashes(blocked_line):
                findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("pythonPath must not be a symlink", messages)
            self.assertNotIn("content appears to reuse a blocked source example", messages)

    def test_cases_reject_known_source_example_fingerprints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            blocked_case = {
                "name": "private denied case",
                "input": {"nums": [31, 41, 59], "target": 90},
                "expected": [0, 2],
            }
            payload["cases"][0] = blocked_case
            write_json(problem / "cases.json", payload)

            with blocked_source_hashes(blocked_case):
                findings = validate_catalog(load_catalog(root), root)

            self.assertIn("appears to reuse a blocked source example", finding_messages(findings))

    def test_cases_reject_blocked_source_fingerprints_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            blocked_case = {
                "name": "private denied case from file",
                "input": {"nums": [26, 53, 58], "target": 84},
                "expected": [0, 2],
            }
            payload["cases"][0] = blocked_case
            write_json(problem / "cases.json", payload)
            hash_file = root / "blocked-source-hashes.txt"
            hash_file.write_text(blocked_source_example_hash(blocked_case) + "\n", encoding="utf-8")
            old_hashes = os.environ.get(BLOCKED_SOURCE_HASHES_ENV)
            old_hash_file = os.environ.get(BLOCKED_SOURCE_HASH_FILE_ENV)
            os.environ.pop(BLOCKED_SOURCE_HASHES_ENV, None)
            os.environ[BLOCKED_SOURCE_HASH_FILE_ENV] = str(hash_file)
            try:
                findings = validate_catalog(load_catalog(root), root)
            finally:
                if old_hashes is None:
                    os.environ.pop(BLOCKED_SOURCE_HASHES_ENV, None)
                else:
                    os.environ[BLOCKED_SOURCE_HASHES_ENV] = old_hashes
                if old_hash_file is None:
                    os.environ.pop(BLOCKED_SOURCE_HASH_FILE_ENV, None)
                else:
                    os.environ[BLOCKED_SOURCE_HASH_FILE_ENV] = old_hash_file

            self.assertIn("appears to reuse a blocked source example", finding_messages(findings))

    def test_blocked_source_hash_file_must_be_readable_when_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid_problem(root)
            old_hashes = os.environ.get(BLOCKED_SOURCE_HASHES_ENV)
            old_hash_file = os.environ.get(BLOCKED_SOURCE_HASH_FILE_ENV)
            os.environ.pop(BLOCKED_SOURCE_HASHES_ENV, None)
            os.environ[BLOCKED_SOURCE_HASH_FILE_ENV] = str(root / "missing-hashes.txt")
            try:
                findings = validate_catalog(load_catalog(root), root)
            finally:
                if old_hashes is None:
                    os.environ.pop(BLOCKED_SOURCE_HASHES_ENV, None)
                else:
                    os.environ[BLOCKED_SOURCE_HASHES_ENV] = old_hashes
                if old_hash_file is None:
                    os.environ.pop(BLOCKED_SOURCE_HASH_FILE_ENV, None)
                else:
                    os.environ[BLOCKED_SOURCE_HASH_FILE_ENV] = old_hash_file

            self.assertIn(
                f"{BLOCKED_SOURCE_HASH_FILE_ENV} is set but cannot be read",
                finding_messages(findings),
            )

    def test_problem_leetcode_metadata_must_match_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json",
                {
                    "collectionId": "leetcode-top-150",
                    "sourceStatus": "pinned",
                    "sourceUrl": "https://leetcode.com/studyplan/top-interview-150/",
                    "snapshotDate": "2026-06-13",
                    "expectedCount": 1,
                    "provenance": {
                        "fetchDate": "2026-06-13",
                        "sourcePages": ["https://leetcode.com/studyplan/top-interview-150/"],
                        "fetchMethod": "websearch-and-public-metadata",
                        "extractorVersion": "test",
                        "metadataSha256": "abc",
                        "reviewReceipt": "test",
                        "rawSourceRetention": "not-retained-copyright-minimization",
                    },
                    "items": [
                        {
                            "sourceId": "1",
                            "title": "Two Sum",
                            "titleSlug": "two-sum",
                            "sourceUrl": "https://leetcode.com/problems/two-sum",
                            "collectionId": "leetcode-top-150",
                            "group": "Array",
                            "order": 1,
                            "difficulty": "easy",
                            "paidOnly": False,
                            "dedupeKey": "leetcode:1:two-sum",
                            "canonicalId": "lc-0001-two-sum",
                        }
                    ],
                },
            )
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["leetcode"]["frontendId"] = "2"
            payload["leetcode"]["url"] = "https://leetcode.com/problems/add-two-numbers"
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("problem.json.leetcode.frontendId must match source manifest metadata", messages)
            self.assertIn("problem.json.leetcode.url must match source manifest metadata", messages)

    def test_problem_leetcode_paid_only_is_required_when_source_manifest_knows_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json",
                {
                    "collectionId": "leetcode-top-150",
                    "sourceStatus": "pinned",
                    "sourceUrl": "https://leetcode.com/studyplan/top-interview-150/",
                    "snapshotDate": "2026-06-13",
                    "expectedCount": 1,
                    "provenance": {
                        "fetchDate": "2026-06-13",
                        "sourcePages": ["https://leetcode.com/studyplan/top-interview-150/"],
                        "fetchMethod": "websearch-and-public-metadata",
                        "extractorVersion": "test",
                        "metadataSha256": "abc",
                        "reviewReceipt": "test",
                        "rawSourceRetention": "not-retained-copyright-minimization",
                    },
                    "items": [
                        {
                            "sourceId": "1",
                            "title": "Two Sum",
                            "titleSlug": "two-sum",
                            "sourceUrl": "https://leetcode.com/problems/two-sum",
                            "collectionId": "leetcode-top-150",
                            "group": "Array",
                            "order": 1,
                            "difficulty": "easy",
                            "paidOnly": False,
                            "dedupeKey": "leetcode:1:two-sum",
                            "canonicalId": "lc-0001-two-sum",
                        }
                    ],
                },
            )
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            del payload["leetcode"]["paidOnly"]
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "problem.json.leetcode.paidOnly must match source manifest metadata",
                finding_messages(findings),
            )

    def test_problem_leetcode_paid_only_must_be_omitted_when_source_manifest_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "neetcode-all.json",
                {
                    "collectionId": "neetcode-all",
                    "sourceStatus": "pinned",
                    "sourceUrl": "https://neetcode.io/practice",
                    "snapshotDate": "2026-06-13",
                    "expectedCount": 1,
                    "provenance": {
                        "fetchDate": "2026-06-13",
                        "sourcePages": ["https://neetcode.io/practice"],
                        "fetchMethod": "websearch-and-public-metadata",
                        "extractorVersion": "test",
                        "metadataSha256": "abc",
                        "reviewReceipt": "test",
                        "rawSourceRetention": "not-retained-copyright-minimization",
                    },
                    "items": [
                        {
                            "sourceId": "1",
                            "title": "Two Sum",
                            "titleSlug": "two-sum",
                            "sourceUrl": "https://leetcode.com/problems/two-sum",
                            "collectionId": "neetcode-all",
                            "group": "Array",
                            "order": 1,
                            "difficulty": "easy",
                            "dedupeKey": "leetcode:1:two-sum",
                            "canonicalId": "lc-0001-two-sum",
                        }
                    ],
                },
            )
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["collections"] = [
                {
                    "id": "neetcode-all",
                    "order": 1,
                    "group": "Array",
                    "sourceUrl": "https://leetcode.com/problems/two-sum",
                }
            ]
            payload["leetcode"]["paidOnly"] = False
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "problem.json.leetcode.paidOnly must be omitted when source manifests do not know access status",
                finding_messages(findings),
            )

    def test_readme_rejects_blocked_source_example_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            blocked_snippet = "private blocked markdown example gamma 161803"
            write_text(
                problem / "README.md",
                "\n".join(
                    [
                        "# Clean-room draft",
                        "",
                        "| Input | Output |",
                        "| --- | --- |",
                        f"| {blocked_snippet} | synthetic output |",
                    ]
                ),
            )

            with blocked_source_hashes(blocked_snippet):
                findings = validate_catalog(load_catalog(root), root)

            self.assertIn("appears to reuse a blocked source example", finding_messages(findings))

    def test_solutions_reject_blocked_examples_and_source_derived_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "solutions.json").read_text(encoding="utf-8"))
            blocked_strategy = "private blocked solution note delta 141421"
            payload["solutions"][0]["strategy"] = blocked_strategy
            payload["solutions"][0]["example"] = {"input": "synthetic input", "output": "synthetic output"}
            write_json(problem / "solutions.json", payload)

            with blocked_source_hashes(blocked_strategy):
                findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("content appears to reuse a blocked source example", messages)
            self.assertIn("contains forbidden source-derived field example", messages)

    def test_problem_json_rejects_source_derived_or_unknown_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["statement"] = "copied prompt text"
            payload["examples"] = ["copied example"]
            payload["leetcode"]["constraints"] = "copied constraints"
            payload["leetcode"]["extra"] = "unexpected metadata"
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("problem.json contains forbidden source-derived field statement", messages)
            self.assertIn("problem.json contains forbidden source-derived field examples", messages)
            self.assertIn("problem.json.leetcode contains forbidden source-derived field constraints", messages)
            self.assertIn("problem.json.leetcode contains unsupported field extra", messages)

    def test_signature_types_must_be_supported_by_generated_drivers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"]["returnType"] = "long"
            payload["signature"]["python"]["parameters"][0]["type"] = "Dict[str, int]"
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("signature.java.returnType is not supported by generated drivers", messages)
            self.assertIn("signature.python.parameters type is not supported by generated drivers", messages)

    def test_signature_types_allow_string_arrays_and_nested_int_arrays(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "merge",
                "returnType": "int[][]",
                "parameters": [
                    {"name": "intervals", "type": "int[][]"},
                    {"name": "labels", "type": "String[]"},
                ],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "merge",
                "returnType": "List[List[int]]",
                "parameters": [
                    {"name": "intervals", "type": "List[List[int]]"},
                    {"name": "labels", "type": "List[str]"},
                ],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0] = {
                "name": "word in first row",
                "input": {"board": [["A", "B"], ["C", "D"]], "word": "AB"},
                "expected": True,
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("not supported by generated drivers", finding_messages(findings))

    def test_signature_types_allow_official_java_list_return_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "threeSum",
                "returnType": "List<List<Integer>>",
                "parameters": [{"name": "nums", "type": "int[]"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "threeSum",
                "returnType": "List[List[int]]",
                "parameters": [{"name": "nums", "type": "List[int]"}],
            }
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("not supported by generated drivers", finding_messages(findings))
            self.assertNotIn("signature java/python return types must be compatible", finding_messages(findings))

    def test_signature_types_allow_float_and_double_driver_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "averages",
                "returnType": "List<Double>",
                "parameters": [{"name": "x", "type": "double"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "averages",
                "returnType": "List[float]",
                "parameters": [{"name": "x", "type": "float"}],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "float-tolerance", "tolerance": 0.000001}
            cases_payload["cases"][0] = {
                "name": "simple average",
                "input": {"x": 2.5},
                "expected": [2.5, -0.0],
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("not supported by generated drivers", finding_messages(findings))
            self.assertNotIn("signature java/python return types must be compatible", finding_messages(findings))
            self.assertNotIn("unsupported matcher", finding_messages(findings))

    def test_signature_types_allow_evaluate_division_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "calcEquation",
                "returnType": "double[]",
                "parameters": [
                    {"name": "equations", "type": "List<List<String>>"},
                    {"name": "values", "type": "double[]"},
                    {"name": "queries", "type": "List<List<String>>"},
                ],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "calcEquation",
                "returnType": "List[float]",
                "parameters": [
                    {"name": "equations", "type": "List[List[str]]"},
                    {"name": "values", "type": "List[float]"},
                    {"name": "queries", "type": "List[List[str]]"},
                ],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "float-tolerance", "tolerance": 0.000001}
            cases_payload["cases"][0] = {
                "name": "division graph",
                "input": {
                    "equations": [["a", "b"], ["b", "c"]],
                    "values": [2.0, 3.0],
                    "queries": [["a", "c"], ["b", "a"], ["x", "x"]],
                },
                "expected": [6.0, 0.5, -1.0],
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("not supported by generated drivers", finding_messages(findings))
            self.assertNotIn("signature java/python return types must be compatible", finding_messages(findings))
            self.assertNotIn("float-tolerance matcher requires a floating return signature", finding_messages(findings))

    def test_function_case_inputs_validate_value_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "calcEquation",
                "returnType": "double[]",
                "parameters": [
                    {"name": "equations", "type": "List<List<String>>"},
                    {"name": "values", "type": "double[]"},
                ],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "calcEquation",
                "returnType": "List[float]",
                "parameters": [
                    {"name": "equations", "type": "List[List[str]]"},
                    {"name": "values", "type": "List[float]"},
                ],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "float-tolerance", "tolerance": 0.000001}
            cases_payload["cases"][0] = {
                "name": "bad function input shapes",
                "input": {"equations": [["a", 5]], "values": [2.0, None]},
                "expected": [1.0],
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("case 1 input.equations must match List<List<String>>/List[List[str]]", messages)
            self.assertIn("case 1 input.values must match double[]/List[float]", messages)

    def test_signature_types_allow_list_node_array_parameter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "mergeKLists",
                "returnType": "ListNode",
                "parameters": [{"name": "lists", "type": "ListNode[]"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "mergeKLists",
                "returnType": "Optional[ListNode]",
                "parameters": [{"name": "lists", "type": "List[Optional[ListNode]]"}],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0] = {
                "name": "three chains",
                "input": {"lists": [[1, 4], None, [2, 3]]},
                "expected": [1, 2, 3, 4],
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("not supported by generated drivers", finding_messages(findings))
            self.assertNotIn("signature java/python parameter types must be compatible", finding_messages(findings))

    def test_list_node_array_is_not_supported_as_return_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "split",
                "returnType": "ListNode[]",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "split",
                "returnType": "List[Optional[ListNode]]",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("signature.java.returnType is not supported by generated drivers", messages)
            self.assertIn("signature.python.returnType is not supported by generated drivers", messages)

    def test_function_case_inputs_validate_list_node_array_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "mergeKLists",
                "returnType": "ListNode",
                "parameters": [{"name": "lists", "type": "ListNode[]"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "mergeKLists",
                "returnType": "Optional[ListNode]",
                "parameters": [{"name": "lists", "type": "List[Optional[ListNode]]"}],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0] = {
                "name": "bad list node array",
                "input": {"lists": [[1, "bad"], 4]},
                "expected": None,
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "case 1 input.lists must match ListNode[]/List[Optional[ListNode]]",
                finding_messages(findings),
            )

    def test_function_case_inputs_allow_cyclic_list_node_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "hasCycle",
                "returnType": "boolean",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "hasCycle",
                "returnType": "bool",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "cycle to middle",
                            "input": {"head": {"values": [6, 1, 8, 5], "cycleTo": 2}},
                            "expected": True,
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_function_case_inputs_reject_malformed_cyclic_list_node_shapes(self) -> None:
        malformed_inputs = [
            {"values": [1, 2], "cycleTo": -1},
            {"values": [1, 2], "cycleTo": 2},
            {"values": [], "cycleTo": 0},
            {"values": [1, "bad"], "cycleTo": 0},
            {"values": [1], "cycleTo": 0, "extra": True},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "hasCycle",
                "returnType": "boolean",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "hasCycle",
                "returnType": "bool",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": f"bad cyclic fixture {index}",
                            "input": {"head": value},
                            "expected": False,
                        }
                        for index, value in enumerate(malformed_inputs, start=1)
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            for index in range(1, len(malformed_inputs) + 1):
                self.assertIn(f"case {index} input.head must match ListNode/Optional[ListNode]", messages)

    def test_unordered_nested_list_matcher_allows_string_nested_list_return_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "groupAnagrams",
                "returnType": "List<List<String>>",
                "parameters": [{"name": "strs", "type": "String[]"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "groupAnagrams",
                "returnType": "List[List[str]]",
                "parameters": [{"name": "strs", "type": "List[str]"}],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "unordered-list-of-lists"}
            cases_payload["cases"][0] = {
                "name": "two groups",
                "input": {"strs": ["arc", "car", "rat"]},
                "expected": [["arc", "car"], ["rat"]],
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("unordered-list-of-lists matcher requires a nested list return signature", finding_messages(findings))
            self.assertNotIn("case 1 expected must be a list of lists matching unordered-list-of-lists return type", finding_messages(findings))

    def test_unordered_nested_list_matcher_allows_integer_matrix_return_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "kClosest",
                "returnType": "int[][]",
                "parameters": [{"name": "points", "type": "int[][]"}, {"name": "k", "type": "int"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "kClosest",
                "returnType": "List[List[int]]",
                "parameters": [{"name": "points", "type": "List[List[int]]"}, {"name": "k", "type": "int"}],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "unordered-list-of-lists"}
            cases_payload["cases"][0] = {
                "name": "unordered points",
                "input": {"points": [[3, 4], [1, 1], [2, 2]], "k": 2},
                "expected": [[1, 1], [2, 2]],
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("unordered-list-of-lists matcher requires a nested list return signature", finding_messages(findings))
            self.assertNotIn("case 1 expected must be a list of lists matching unordered-list-of-lists return type", finding_messages(findings))

    def test_float_tolerance_matcher_requires_explicit_finite_tolerance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "myPow",
                "returnType": "double",
                "parameters": [{"name": "x", "type": "double"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "myPow",
                "returnType": "float",
                "parameters": [{"name": "x", "type": "float"}],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "float-tolerance"}
            cases_payload["cases"][0] = {
                "name": "double output",
                "input": {"x": 2.0},
                "expected": 4.0,
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("float-tolerance matcher requires a positive finite tolerance", finding_messages(findings))

    def test_floating_return_signature_requires_float_tolerance_matcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "median",
                "returnType": "double",
                "parameters": [{"name": "nums", "type": "int[]"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "median",
                "returnType": "float",
                "parameters": [{"name": "nums", "type": "List[int]"}],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "exact"}
            cases_payload["cases"][0] = {
                "name": "floating output",
                "input": {"nums": [1, 2]},
                "expected": 1.5,
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("floating return signatures require float-tolerance matcher", finding_messages(findings))

    def test_signature_types_allow_official_java_list_parameter_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "wordBreak",
                "returnType": "boolean",
                "parameters": [
                    {"name": "s", "type": "String"},
                    {"name": "wordDict", "type": "List<String>"},
                    {"name": "costs", "type": "List<Integer>"},
                    {"name": "weights", "type": "List<Double>"},
                    {"name": "triangle", "type": "List<List<Integer>>"},
                ],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "wordBreak",
                "returnType": "bool",
                "parameters": [
                    {"name": "s", "type": "str"},
                    {"name": "wordDict", "type": "List[str]"},
                    {"name": "costs", "type": "List[int]"},
                    {"name": "weights", "type": "List[float]"},
                    {"name": "triangle", "type": "List[List[int]]"},
                ],
            }
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("not supported by generated drivers", finding_messages(findings))
            self.assertNotIn("signature java/python parameter types must be compatible", finding_messages(findings))

    def test_object_operation_signature_and_cases_are_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "MinStack",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "push", "returnType": "void", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "pop", "returnType": "void", "parameters": []},
                        {"name": "top", "returnType": "int", "parameters": []},
                        {"name": "getMin", "returnType": "int", "parameters": []}
                    ]
                },
                "python": {
                    "className": "MinStack",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "push", "returnType": "None", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "pop", "returnType": "None", "parameters": []},
                        {"name": "top", "returnType": "int", "parameters": []},
                        {"name": "getMin", "returnType": "int", "parameters": []}
                    ]
                }
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "push pop and min",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "push", "input": {"val": 3}, "expected": None},
                                {"type": "call", "method": "push", "input": {"val": 1}, "expected": None},
                                {"type": "call", "method": "getMin", "input": {}, "expected": 1},
                                {"type": "call", "method": "pop", "input": {}, "expected": None},
                                {"type": "call", "method": "top", "input": {}, "expected": 3}
                            ]
                        }
                    ]
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_object_operation_cases_validate_method_registry_and_constructor_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "MinStack",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "push", "returnType": "void", "parameters": [{"name": "val", "type": "int"}]}
                    ],
                },
                "python": {
                    "className": "MinStack",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "push", "returnType": "None", "parameters": [{"name": "val", "type": "int"}]}
                    ],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "unsafe operation names",
                            "operations": [
                                {"type": "call", "method": "peekMin", "input": {}, "expected": 0},
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "push", "input": {}, "expected": None},
                            ],
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("case 1 first operation must be constructor", messages)
            self.assertIn("case 1 constructor operation must be first", messages)
            self.assertIn("case 1 operation peekMin is not defined by object signature", messages)
            self.assertIn("case 1 operation 3 missing input val", messages)

    def test_object_operation_expected_key_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "Counter",
                    "constructor": {"parameters": []},
                    "methods": [{"name": "value", "returnType": "int", "parameters": []}],
                },
                "python": {
                    "className": "Counter",
                    "constructor": {"parameters": []},
                    "methods": [{"name": "value", "returnType": "int", "parameters": []}],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "missing expected",
                            "operations": [
                                {"type": "constructor", "input": {}},
                                {"type": "call", "method": "value", "input": {}},
                            ],
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("case 1 operation 1 expected is required", messages)
            self.assertIn("case 1 operation 2 expected is required", messages)

    def test_object_one_of_matcher_validates_int_expected_sets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "RandomizedSet",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "insert", "returnType": "boolean", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "getRandom", "returnType": "int", "parameters": []},
                    ],
                },
                "python": {
                    "className": "RandomizedSet",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "insert", "returnType": "bool", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "getRandom", "returnType": "int", "parameters": []},
                    ],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "object-one-of"},
                    "cases": [
                        {
                            "name": "member result",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "insert", "input": {"val": 10}, "expected": True},
                                {"type": "call", "method": "insert", "input": {"val": 20}, "expected": True},
                                {"type": "call", "method": "getRandom", "input": {}, "expected": {"oneOf": [10, 20]}},
                            ],
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("expected must match method return type", finding_messages(findings))

    def test_object_one_of_matcher_rejects_invalid_expected_sets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "RandomizedSet",
                    "constructor": {"parameters": []},
                    "methods": [{"name": "getRandom", "returnType": "int", "parameters": []}],
                },
                "python": {
                    "className": "RandomizedSet",
                    "constructor": {"parameters": []},
                    "methods": [{"name": "getRandom", "returnType": "int", "parameters": []}],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "object-one-of"},
                    "cases": [
                        {
                            "name": "bad allowed values",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "getRandom", "input": {}, "expected": {"oneOf": []}},
                            ],
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("case 1 operation 2 expected must match method return type", finding_messages(findings))

    def test_object_one_of_matcher_is_object_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["matcher"] = {"type": "object-one-of"}
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("object-one-of matcher requires object operation cases", finding_messages(findings))

    def test_object_operation_inputs_validate_value_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "Counter",
                    "constructor": {"parameters": [{"name": "start", "type": "int"}]},
                    "methods": [
                        {"name": "add", "returnType": "void", "parameters": [{"name": "delta", "type": "int"}]},
                        {"name": "value", "returnType": "int", "parameters": []},
                    ],
                },
                "python": {
                    "className": "Counter",
                    "constructor": {"parameters": [{"name": "start", "type": "int"}]},
                    "methods": [
                        {"name": "add", "returnType": "None", "parameters": [{"name": "delta", "type": "int"}]},
                        {"name": "value", "returnType": "int", "parameters": []},
                    ],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "bad scalar types",
                            "operations": [
                                {"type": "constructor", "input": {"start": True}, "expected": None},
                                {"type": "call", "method": "add", "input": {"delta": "3"}, "expected": None},
                                {"type": "call", "method": "value", "input": {}, "expected": 0},
                            ],
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("case 1 operation 1 input.start must match int/int", messages)
            self.assertIn("case 1 operation 2 input.delta must match int/int", messages)

    def test_object_operation_inputs_allow_supported_container_and_node_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "ShapeSink",
                    "constructor": {"parameters": [{"name": "root", "type": "TreeNode"}]},
                    "methods": [
                        {
                            "name": "accept",
                            "returnType": "void",
                            "parameters": [
                                {"name": "nums", "type": "int[]"},
                                {"name": "intervals", "type": "int[][]"},
                                {"name": "board", "type": "char[][]"},
                                {"name": "words", "type": "List<String>"},
                                {"name": "pairs", "type": "List<List<Integer>>"},
                                {"name": "head", "type": "ListNode"},
                            ],
                        }
                    ],
                },
                "python": {
                    "className": "ShapeSink",
                    "constructor": {"parameters": [{"name": "root", "type": "Optional[TreeNode]"}]},
                    "methods": [
                        {
                            "name": "accept",
                            "returnType": "None",
                            "parameters": [
                                {"name": "nums", "type": "List[int]"},
                                {"name": "intervals", "type": "List[List[int]]"},
                                {"name": "board", "type": "List[List[str]]"},
                                {"name": "words", "type": "List[str]"},
                                {"name": "pairs", "type": "List[List[int]]"},
                                {"name": "head", "type": "Optional[ListNode]"},
                            ],
                        }
                    ],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "all supported shapes",
                            "operations": [
                                {"type": "constructor", "input": {"root": [2, None, 3]}, "expected": None},
                                {
                                    "type": "call",
                                    "method": "accept",
                                    "input": {
                                        "nums": [1, 2],
                                        "intervals": [[1, 2], [3, 4]],
                                        "board": [["a", "b"], ["c", "d"]],
                                        "words": ["left", "right"],
                                        "pairs": [[5, 6]],
                                        "head": [7, 8],
                                    },
                                    "expected": None,
                                },
                            ],
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_object_float_tolerance_allows_mixed_return_methods(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "Stats",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "count", "returnType": "int", "parameters": []},
                        {"name": "average", "returnType": "double", "parameters": []},
                    ],
                },
                "python": {
                    "className": "Stats",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "count", "returnType": "int", "parameters": []},
                        {"name": "average", "returnType": "float", "parameters": []},
                    ],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "float-tolerance", "tolerance": 0.001},
                    "cases": [
                        {
                            "name": "mixed returns",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "count", "input": {}, "expected": 2},
                                {"type": "call", "method": "average", "input": {}, "expected": 2.5},
                            ],
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_signature_types_allow_char_grid_parameters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "exist",
                "returnType": "boolean",
                "parameters": [
                    {"name": "board", "type": "char[][]"},
                    {"name": "word", "type": "String"},
                ],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "exist",
                "returnType": "bool",
                "parameters": [
                    {"name": "board", "type": "List[List[str]]"},
                    {"name": "word", "type": "str"},
                ],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0] = {
                "name": "word in first row",
                "input": {"board": [["A", "B"], ["C", "D"]], "word": "AB"},
                "expected": True,
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("not supported by generated drivers", finding_messages(findings))
            self.assertEqual([], findings, finding_messages(findings))

    def test_signature_types_allow_scalar_char_parameters_and_returns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "echo",
                "returnType": "char",
                "parameters": [{"name": "letter", "type": "char"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "echo",
                "returnType": "str",
                "parameters": [{"name": "letter", "type": "str"}],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0] = {
                "name": "single character",
                "input": {"letter": "z"},
                "expected": "z",
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_signature_types_reject_invalid_scalar_char_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "echo",
                "returnType": "char",
                "parameters": [{"name": "letter", "type": "char"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "echo",
                "returnType": "str",
                "parameters": [{"name": "letter", "type": "str"}],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0] = {
                "name": "not a scalar character",
                "input": {"letter": "ab"},
                "expected": "",
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("case 1 input.letter must match char/str", messages)
            self.assertIn("case 1 expected must match char/str", messages)

    def test_signature_types_allow_void_and_none_for_mutation_drivers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "merge",
                "returnType": "void",
                "parameters": [
                    {"name": "nums1", "type": "int[]"},
                    {"name": "m", "type": "int"},
                    {"name": "nums2", "type": "int[]"},
                    {"name": "n", "type": "int"},
                ],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "merge",
                "returnType": "None",
                "parameters": [
                    {"name": "nums1", "type": "List[int]"},
                    {"name": "m", "type": "int"},
                    {"name": "nums2", "type": "List[int]"},
                    {"name": "n", "type": "int"},
                ],
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "merge into first buffer",
                            "input": {"nums1": [2, 5, 0, 0], "m": 2, "nums2": [1, 6], "n": 2},
                            "expected": None,
                            "expectedMutations": {"nums1": [1, 2, 5, 6]},
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("not supported by generated drivers", finding_messages(findings))
            self.assertEqual([], findings, finding_messages(findings))

    def test_signature_types_allow_official_list_node_signatures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "ListNode",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "Optional[ListNode]",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "reverse compact chain",
                            "input": {"head": [4, 1, 9]},
                            "expected": [9, 1, 4],
                            "linkedListContract": {
                                "result": {"from": "head", "nodeIndices": [2, 1, 0]}
                            },
                        },
                        {
                            "name": "empty chain",
                            "input": {"head": None},
                            "expected": None,
                        },
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("not supported by generated drivers", finding_messages(findings))
            self.assertEqual([], findings, finding_messages(findings))

    def test_signature_types_allow_official_tree_node_signatures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "isSameTree",
                "returnType": "boolean",
                "parameters": [
                    {"name": "p", "type": "TreeNode"},
                    {"name": "q", "type": "TreeNode"},
                ],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "isSameTree",
                "returnType": "bool",
                "parameters": [
                    {"name": "p", "type": "Optional[TreeNode]"},
                    {"name": "q", "type": "Optional[TreeNode]"},
                ],
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "different branch value",
                            "input": {"p": [4, 2, 7], "q": [4, 2, 8]},
                            "expected": False,
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertNotIn("not supported by generated drivers", finding_messages(findings))
            self.assertEqual([], findings, finding_messages(findings))

    def test_signature_types_allow_binary_tree_next_node_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "customTypes": {"Node": "binary-tree-next"},
                "java": {
                    "className": "Solution",
                    "methodName": "connect",
                    "returnType": "Node",
                    "parameters": [{"name": "root", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "connect",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "root", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "ragged next levels",
                            "input": {"root": [1, 2, 3, None, 4, None, 5]},
                            "expected": [[1], [2, 3], [4, 5]],
                            "expectedMutations": {"root": [[1], [2, 3], [4, 5]]},
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_binary_tree_next_node_signature_requires_custom_type_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "connect",
                "returnType": "Node",
                "parameters": [{"name": "root", "type": "Node"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "connect",
                "returnType": "Optional[Node]",
                "parameters": [{"name": "root", "type": "Optional[Node]"}],
            }
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("signature.customTypes.Node is required when generated drivers use Node", finding_messages(findings))

    def test_object_signature_rejects_node_without_custom_type_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "NodeBox",
                    "constructor": {"parameters": [{"name": "root", "type": "Node"}]},
                    "methods": [
                        {"name": "peek", "returnType": "Node", "parameters": []}
                    ],
                },
                "python": {
                    "className": "NodeBox",
                    "constructor": {"parameters": [{"name": "root", "type": "Optional[Node]"}]},
                    "methods": [
                        {"name": "peek", "returnType": "Optional[Node]", "parameters": []}
                    ],
                },
            }
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("signature.customTypes.Node is required when generated drivers use Node", finding_messages(findings))

    def test_binary_tree_next_node_mutations_require_next_level_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "customTypes": {"Node": "binary-tree-next"},
                "java": {
                    "className": "Solution",
                    "methodName": "connect",
                    "returnType": "Node",
                    "parameters": [{"name": "root", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "connect",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "root", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "bad mutation shape",
                            "input": {"root": [1, 2, 3]},
                            "expected": [[1], [2, 3]],
                            "expectedMutations": {"root": [1, 2, 3]},
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("case 1 expectedMutations.root must match Node/Optional[Node] next-level values", finding_messages(findings))

    def test_signature_types_allow_random_list_node_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "customTypes": {"Node": "random-list"},
                "java": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Node",
                    "parameters": [{"name": "head", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "head", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "random pointers by index",
                            "input": {"head": [[8, None], [12, 0], [5, 2]]},
                            "expected": [[8, None], [12, 0], [5, 2]],
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_expected_mutations_allow_random_list_node_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "customTypes": {"Node": "random-list"},
                "java": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Node",
                    "parameters": [{"name": "head", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "head", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "copy and preserve original",
                            "input": {"head": [[8, None], [12, 0]]},
                            "expected": [[8, None], [12, 0]],
                            "expectedMutations": {"head": [[8, None], [12, 0]]},
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_signature_types_allow_graph_node_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "customTypes": {"Node": "graph"},
                "java": {
                    "className": "Solution",
                    "methodName": "cloneGraph",
                    "returnType": "Node",
                    "parameters": [{"name": "node", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "cloneGraph",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "node", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "triangle",
                            "input": {"node": [[2, 3], [1, 3], [1, 2]]},
                            "expected": [[2, 3], [1, 3], [1, 2]],
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_signature_types_allow_quad_tree_node_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "customTypes": {"Node": "quad-tree"},
                "java": {
                    "className": "Solution",
                    "methodName": "construct",
                    "returnType": "Node",
                    "parameters": [{"name": "grid", "type": "int[][]"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "construct",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "grid", "type": "List[List[int]]"}],
                },
            }
            expected = {
                "val": True,
                "isLeaf": False,
                "topLeft": {"val": True, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
                "topRight": {"val": False, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
                "bottomLeft": {"val": False, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
                "bottomRight": {"val": True, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "mixed quadrants",
                            "input": {"grid": [[1, 0], [0, 1]]},
                            "expected": expected,
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_quad_tree_signature_rejects_node_parameters_until_drivers_support_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "customTypes": {"Node": "quad-tree"},
                "java": {
                    "className": "Solution",
                    "methodName": "copy",
                    "returnType": "Node",
                    "parameters": [{"name": "root", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "copy",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "root", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "unsupported quad-tree input",
                            "input": {"root": quad_tree_leaf(True)},
                            "expected": quad_tree_leaf(True),
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "signature.customTypes.Node quad-tree currently supports Node returns only",
                finding_messages(findings),
            )

    def test_quad_tree_expected_rejects_leaf_with_children(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "customTypes": {"Node": "quad-tree"},
                "java": {
                    "className": "Solution",
                    "methodName": "construct",
                    "returnType": "Node",
                    "parameters": [{"name": "grid", "type": "int[][]"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "construct",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "grid", "type": "List[List[int]]"}],
                },
            }
            malformed = quad_tree_leaf(True)
            malformed["topLeft"] = quad_tree_leaf(False)
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "leaf with child",
                            "input": {"grid": [[1]]},
                            "expected": malformed,
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("case 1 expected must match Node/Optional[Node]", finding_messages(findings))

    def test_quad_tree_expected_rejects_internal_node_with_missing_child(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "customTypes": {"Node": "quad-tree"},
                "java": {
                    "className": "Solution",
                    "methodName": "construct",
                    "returnType": "Node",
                    "parameters": [{"name": "grid", "type": "int[][]"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "construct",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "grid", "type": "List[List[int]]"}],
                },
            }
            malformed = quad_tree_node(
                quad_tree_leaf(True),
                quad_tree_leaf(False),
                None,
                quad_tree_leaf(True),
            )
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "internal with missing child",
                            "input": {"grid": [[1, 0], [0, 1]]},
                            "expected": malformed,
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("case 1 expected must match Node/Optional[Node]", finding_messages(findings))

    def test_graph_node_cases_reject_disconnected_adjacency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"] = {
                "customTypes": {"Node": "graph"},
                "java": {
                    "className": "Solution",
                    "methodName": "cloneGraph",
                    "returnType": "Node",
                    "parameters": [{"name": "node", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "cloneGraph",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "node", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "disconnected",
                            "input": {"node": [[], []]},
                            "expected": [[], []],
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("case 1 input.node must match Node/Optional[Node]", finding_messages(findings))

    def test_function_case_inputs_allow_tree_node_identity_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "TreeNode",
                "parameters": [
                    {"name": "root", "type": "TreeNode"},
                    {"name": "p", "type": "TreeNode"},
                    {"name": "q", "type": "TreeNode"},
                ],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "Optional[TreeNode]",
                "parameters": [
                    {"name": "root", "type": "Optional[TreeNode]"},
                    {"name": "p", "type": "Optional[TreeNode]"},
                    {"name": "q", "type": "Optional[TreeNode]"},
                ],
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "lca from existing nodes",
                            "input": {
                                "root": [9, 4, 13, 2, 6, 11, 15, None, 3, 5, 7],
                                "p": {"from": "root", "path": "LLR"},
                                "q": {"from": "root", "path": "LRL"},
                            },
                            "expected": {"from": "root", "path": "L"},
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_function_case_inputs_reject_invalid_tree_node_references(self) -> None:
        invalid_cases = [
            (
                "unknown source",
                {"root": [1, 2, 3], "p": {"from": "missing", "path": "L"}, "q": {"from": "root", "path": "R"}},
                {"from": "root", "path": ""},
                "case 1 input.p.from must name a signature parameter",
            ),
            (
                "forward source",
                {"root": {"from": "p", "path": ""}, "p": [1], "q": {"from": "p", "path": ""}},
                {"from": "p", "path": ""},
                "case 2 input.root.from must reference an earlier TreeNode parameter",
            ),
            (
                "missing path",
                {"root": [1, None, 3], "p": {"from": "root", "path": "L"}, "q": {"from": "root", "path": "R"}},
                {"from": "root", "path": ""},
                "case 3 input.p.path does not resolve to a TreeNode",
            ),
            (
                "bad expected path",
                {"root": [1, 2, 3], "p": {"from": "root", "path": "L"}, "q": {"from": "root", "path": "R"}},
                {"from": "root", "path": "LL"},
                "case 4 expected.path does not resolve to a TreeNode",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "TreeNode",
                "parameters": [
                    {"name": "root", "type": "TreeNode"},
                    {"name": "p", "type": "TreeNode"},
                    {"name": "q", "type": "TreeNode"},
                ],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "Optional[TreeNode]",
                "parameters": [
                    {"name": "root", "type": "Optional[TreeNode]"},
                    {"name": "p", "type": "Optional[TreeNode]"},
                    {"name": "q", "type": "Optional[TreeNode]"},
                ],
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": name,
                            "input": input_value,
                            "expected": expected,
                        }
                        for name, input_value, expected, _ in invalid_cases
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            for _, _, _, expected_message in invalid_cases:
                self.assertIn(expected_message, messages)

    def test_function_case_expected_rejects_malformed_tree_node_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "invertTree",
                "returnType": "TreeNode",
                "parameters": [{"name": "root", "type": "TreeNode"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "invertTree",
                "returnType": "Optional[TreeNode]",
                "parameters": [{"name": "root", "type": "Optional[TreeNode]"}],
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {"name": "bad scalar", "input": {"root": [1]}, "expected": 1},
                        {"name": "bad object", "input": {"root": [1]}, "expected": {"path": ""}},
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("case 1 expected must match TreeNode/Optional[TreeNode]", messages)
            self.assertIn("case 2 expected must match TreeNode/Optional[TreeNode]", messages)

    def test_function_case_inputs_reject_unreachable_tree_node_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "invertTree",
                "returnType": "TreeNode",
                "parameters": [{"name": "root", "type": "TreeNode"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "invertTree",
                "returnType": "Optional[TreeNode]",
                "parameters": [{"name": "root", "type": "Optional[TreeNode]"}],
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {"name": "null root descendants", "input": {"root": [None, 1]}, "expected": []},
                        {"name": "unreachable value", "input": {"root": [1, None, None, 2]}, "expected": [1]},
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("case 1 input.root must match TreeNode/Optional[TreeNode]", messages)
            self.assertIn("case 2 input.root must match TreeNode/Optional[TreeNode]", messages)

    def test_expected_mutations_allow_tree_node_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "flatten",
                "returnType": "void",
                "parameters": [{"name": "root", "type": "TreeNode"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "flatten",
                "returnType": "None",
                "parameters": [{"name": "root", "type": "Optional[TreeNode]"}],
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "flatten mutation",
                            "input": {"root": [1, 2, 3]},
                            "expected": None,
                            "expectedMutations": {"root": [1, None, 2, None, 3]},
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertEqual([], findings, finding_messages(findings))

    def test_expected_mutations_reject_malformed_tree_node_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "flatten",
                "returnType": "void",
                "parameters": [{"name": "root", "type": "TreeNode"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "flatten",
                "returnType": "None",
                "parameters": [{"name": "root", "type": "Optional[TreeNode]"}],
            }
            write_json(problem / "problem.json", payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "bad tree mutation",
                            "input": {"root": [1, 2, 3]},
                            "expected": None,
                            "expectedMutations": {"root": [None, 1]},
                        }
                    ],
                },
            )

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "case 1 expectedMutations.root must match TreeNode/Optional[TreeNode]",
                finding_messages(findings),
            )

    def test_tree_node_return_cases_use_empty_list_for_empty_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "invertTree",
                "returnType": "TreeNode",
                "parameters": [{"name": "root", "type": "TreeNode"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "invertTree",
                "returnType": "Optional[TreeNode]",
                "parameters": [{"name": "root", "type": "Optional[TreeNode]"}],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0] = {
                "name": "empty tree",
                "input": {"root": []},
                "expected": None,
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "case 1 expected must use [] for an empty TreeNode result",
                finding_messages(findings),
            )

    def test_linked_list_contract_must_reference_list_node_indices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0]["linkedListContract"] = {
                "result": {"from": "nums", "nodeIndices": [0, 99]},
                "postCall": {"target": [0]},
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("case 1 linkedListContract.result.from must target a ListNode parameter", messages)
            self.assertIn("case 1 linkedListContract.result requires a ListNode return signature", messages)
            self.assertIn("case 1 linkedListContract.result.nodeIndices contains an out-of-range node index", messages)
            self.assertIn("case 1 linkedListContract.postCall.target must target a ListNode parameter", messages)

    def test_linked_list_contract_rejects_cyclic_input_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "isPalindrome",
                "returnType": "boolean",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "isPalindrome",
                "returnType": "bool",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0] = {
                "name": "cyclic input with post-call identity contract",
                "input": {"head": {"values": [6, 1, 8, 5], "cycleTo": 2}},
                "expected": False,
                "linkedListContract": {"postCall": {"head": [0, 1, 2, 3]}},
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "case 1 linkedListContract.postCall.head cannot reference cyclic ListNode input",
                finding_messages(findings),
            )

    def test_linked_list_contract_rejects_boolean_node_indices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "ListNode",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "Optional[ListNode]",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0] = {
                "name": "boolean index",
                "input": {"head": [1, 2]},
                "expected": [2, 1],
                "linkedListContract": {"result": {"from": "head", "nodeIndices": [True, 0]}},
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn(
                "case 1 linkedListContract.result.nodeIndices must be a list of non-negative integer indices",
                finding_messages(findings),
            )

    def test_void_cases_require_expected_mutations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"]["returnType"] = "void"
            problem_payload["signature"]["python"]["returnType"] = "None"
            write_json(problem / "problem.json", problem_payload)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0]["expected"] = None
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("case 1 expectedMutations is required for void/None return signatures", finding_messages(findings))

    def test_expected_mutation_prefix_must_reference_input_and_length(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0]["expectedMutations"] = {
                "missing": {"prefix": [4, 6], "lengthFrom": "answer"}
            }
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("case 1 expectedMutations.missing must name a signature parameter", messages)
            self.assertIn("case 1 expectedMutations.missing lengthFrom must be return", messages)

    def test_cases_reject_unknown_case_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0]["sourceExample"] = "not allowed"
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("case 1 contains unsupported field sourceExample", finding_messages(findings))

    def test_cases_reject_extra_input_keys_not_used_by_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"][0]["input"]["copiedOfficialExample"] = {"nums": [1, 2, 3]}
            write_json(problem / "cases.json", cases_payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("case 1 input contains unsupported key copiedOfficialExample", finding_messages(findings))

    def test_signature_parameters_must_match_between_languages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"]["parameters"][0]["name"] = "values"
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("signature java/python parameter names must match for generated drivers", finding_messages(findings))

    def test_signature_identifiers_must_be_safe_for_generated_drivers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            payload["signature"]["java"]["methodName"] = "twoSum);"
            payload["signature"]["python"]["methodName"] = "twoSum);"
            payload["signature"]["java"]["parameters"][0]["name"] = "nums;"
            payload["signature"]["python"]["parameters"][0]["name"] = "nums;"
            write_json(problem / "problem.json", payload)

            findings = validate_catalog(load_catalog(root), root)
            messages = finding_messages(findings)

            self.assertIn("signature.java.methodName must be a safe identifier", messages)
            self.assertIn("signature.python.methodName must be a safe identifier", messages)
            self.assertIn("signature.java.parameters name must be a safe identifier", messages)
            self.assertIn("signature.python.parameters name must be a safe identifier", messages)

    def test_collection_membership_must_match_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid_problem(root)
            manifest = valid_source_manifest()
            manifest["items"][0]["order"] = 99
            manifest["provenance"]["metadataSha256"] = source_metadata_hash(manifest["items"])
            write_json(root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json", manifest)

            findings = validate_catalog(load_catalog(root), root)

            self.assertIn("collection leetcode-top-150 order must match source manifest", finding_messages(findings))

    def test_collection_membership_must_include_all_source_manifest_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid_problem(root)
            leetcode = valid_source_manifest("leetcode-top-150")
            grind = valid_source_manifest("grind-169")
            write_json(root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json", leetcode)
            write_json(root / "resources" / "source-intake" / "coding-lists" / "grind-169.json", grind)

            findings = validate_catalog(load_catalog(root), root, require_source_manifests=True)

            self.assertIn("missing collection membership grind-169 from source manifests", finding_messages(findings))


class SourceManifestValidationTest(unittest.TestCase):
    def test_source_manifest_loader_ignores_symlinked_source_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = Path(tmp) / "outside-sources"
            write_json(
                outside / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json",
                valid_source_manifest("leetcode-top-150"),
            )
            source_parent = root / "resources" / "source-intake"
            source_parent.mkdir(parents=True)
            (source_parent / "coding-lists").symlink_to(
                outside / "resources" / "source-intake" / "coding-lists",
                target_is_directory=True,
            )

            self.assertEqual([], load_source_manifests(root))

    def test_collection_filter_skips_unrelated_invalid_source_manifests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json",
                valid_source_manifest("leetcode-top-150"),
            )
            write_json(root / "resources" / "source-intake" / "coding-lists" / "grind-169.json", ["not an object"])
            unrelated = valid_source_manifest("neetcode-all")
            unrelated["statement"] = "copied source text"
            unrelated["sourceUrl"] = "http://example.com/bad"
            write_json(root / "resources" / "source-intake" / "coding-lists" / "neetcode-all.json", unrelated)

            findings = validate_source_manifests(
                load_source_manifests(root),
                collection="leetcode-top-150",
            )

            self.assertEqual([], findings, finding_messages(findings))

    def test_collection_cli_skips_unrelated_malformed_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json",
                valid_source_manifest("leetcode-top-150"),
            )
            write_text(root / "resources" / "source-intake" / "coding-lists" / "grind-169.json", "{not json")

            result = run_python_command(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "check_coding_problem_catalog.py"),
                    "--root",
                    str(root),
                    "--sources",
                    "--collection",
                    "leetcode-top-150",
                ],
                REPO_ROOT,
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("PASS coding problem catalog", result.stdout)

    def test_collection_cli_reports_missing_requested_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json",
                valid_source_manifest("leetcode-top-150"),
            )

            result = run_python_command(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "check_coding_problem_catalog.py"),
                    "--root",
                    str(root),
                    "--sources",
                    "--collection",
                    "does-not-exist",
                ],
                REPO_ROOT,
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("source manifest for collection does-not-exist is missing", result.stdout)

    def test_collection_filter_reports_requested_malformed_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_text(root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json", "{not json")
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "grind-169.json",
                valid_source_manifest("grind-169"),
            )

            findings = validate_source_manifests(
                load_source_manifests(root, collection="leetcode-top-150"),
                collection="leetcode-top-150",
            )

            self.assertIn("source manifest JSON is invalid", finding_messages(findings))

    def test_source_manifest_requires_provenance_with_matching_metadata_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = valid_source_manifest()
            manifest.pop("provenance")
            write_json(root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json", manifest)

            findings = validate_source_manifests(load_source_manifests(root))

            self.assertIn("pinned source manifest must define provenance", finding_messages(findings))

            manifest = valid_source_manifest()
            manifest["provenance"]["metadataSha256"] = "bad"
            write_json(root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json", manifest)

            findings = validate_source_manifests(load_source_manifests(root))

            self.assertIn("provenance.metadataSha256 must match the normalized items payload", finding_messages(findings))

    def test_source_manifest_requires_snapshot_date_and_url_source_pages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = valid_source_manifest()
            manifest.pop("snapshotDate")
            manifest["provenance"]["sourcePages"] = ["not-a-url"]
            write_json(root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json", manifest)

            findings = validate_source_manifests(load_source_manifests(root))
            messages = finding_messages(findings)

            self.assertIn("snapshotDate must be an ISO date", messages)
            self.assertIn("provenance.sourcePages[1] must use https and an allowed host", messages)

    def test_source_manifest_rejects_unexpected_collection_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = valid_source_manifest("grind-169")
            manifest["sourceUrl"] = "https://www.techinterviewhandbook.org/algorithms/"
            manifest["provenance"]["sourcePages"] = [manifest["sourceUrl"]]
            write_json(root / "resources" / "source-intake" / "coding-lists" / "grind-169.json", manifest)

            findings = validate_source_manifests(load_source_manifests(root))

            self.assertIn("sourceUrl for grind-169 must be https://www.techinterviewhandbook.org/grind75/", finding_messages(findings))

    def test_source_manifest_expected_count_must_match_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json",
                {
                    "collectionId": "leetcode-top-150",
                    "sourceStatus": "pinned",
                    "sourceUrl": "https://leetcode.com/studyplan/top-interview-150/",
                    "expectedCount": 2,
                    "items": [
                        {
                            "sourceId": "1",
                            "title": "Two Sum",
                            "titleSlug": "two-sum",
                            "sourceUrl": "https://leetcode.com/problems/two-sum",
                            "collectionId": "leetcode-top-150",
                            "group": "Hashmap",
                            "order": 1,
                            "difficulty": "easy",
                            "dedupeKey": "leetcode:1:two-sum",
                            "canonicalId": "lc-0001-two-sum",
                        }
                    ],
                },
            )

            findings = validate_source_manifests(load_source_manifests(root))

            self.assertIn("expectedCount 2 does not match item count 1", finding_messages(findings))

    def test_source_manifest_rejects_statement_like_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json",
                {
                    "collectionId": "leetcode-top-150",
                    "sourceStatus": "pinned",
                    "sourceUrl": "https://leetcode.com/studyplan/top-interview-150/",
                    "expectedCount": 1,
                    "items": [
                        {
                            "sourceId": "1",
                            "title": "Two Sum",
                            "titleSlug": "two-sum",
                            "sourceUrl": "https://leetcode.com/problems/two-sum",
                            "collectionId": "leetcode-top-150",
                            "group": "Hashmap",
                            "order": 1,
                            "difficulty": "easy",
                            "dedupeKey": "leetcode:1:two-sum",
                            "canonicalId": "lc-0001-two-sum",
                            "statement": "copied problem text",
                        }
                    ],
                },
            )

            findings = validate_source_manifests(load_source_manifests(root))

            self.assertIn("forbidden source-derived field statement", finding_messages(findings))

    def test_source_manifest_rejects_non_metadata_sized_display_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = valid_source_manifest()
            item = manifest["items"][0]
            item["sourceId"] = "one"
            item["titleSlug"] = "Two Sum"
            item["title"] = "[Two Sum](https://leetcode.com/problems/two-sum)"
            item["group"] = "<b>Hashmap</b>"
            item["difficulty"] = "introductory"
            manifest["provenance"]["metadataSha256"] = source_metadata_hash(manifest["items"])
            write_json(root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json", manifest)

            findings = validate_source_manifests(load_source_manifests(root))
            messages = finding_messages(findings)

            self.assertIn("item 1 sourceId must be numeric LeetCode metadata", messages)
            self.assertIn("item 1 titleSlug must be a lowercase URL slug", messages)
            self.assertIn("item 1 title must be plain metadata text", messages)
            self.assertIn("item 1 group must be plain metadata text", messages)
            self.assertIn("item 1 difficulty must be one of", messages)

    def test_source_manifest_requires_scaffold_and_collection_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json",
                {
                    "collectionId": "leetcode-top-150",
                    "sourceStatus": "pinned",
                    "sourceUrl": "https://leetcode.com/studyplan/top-interview-150/",
                    "expectedCount": 1,
                    "items": [
                        {
                            "sourceId": "1",
                            "title": "Two Sum",
                            "sourceUrl": "https://leetcode.com/problems/two-sum",
                            "collectionId": "leetcode-top-150",
                            "order": 1,
                        }
                    ],
                },
            )

            findings = validate_source_manifests(load_source_manifests(root))
            messages = finding_messages(findings)

            self.assertIn("item 1 missing titleSlug", messages)
            self.assertIn("item 1 missing canonicalId", messages)
            self.assertIn("item 1 missing dedupeKey", messages)

    def test_source_manifest_rejects_inconsistent_leetcode_canonical_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "grind-169.json",
                {
                    "collectionId": "grind-169",
                    "sourceStatus": "pinned",
                    "sourceUrl": "https://www.techinterviewhandbook.org/grind75/",
                    "expectedCount": 1,
                    "items": [
                        {
                            "sourceId": "704",
                            "title": "Binary Search",
                            "titleSlug": "binary-search",
                            "sourceUrl": "https://leetcode.com/problems/binary-search",
                            "collectionId": "grind-169",
                            "order": 1,
                            "canonicalId": "lc-0792-binary-search",
                            "dedupeKey": "leetcode:704:binary-search",
                        }
                    ],
                },
            )

            findings = validate_source_manifests(load_source_manifests(root))

            self.assertIn("canonicalId must be lc-0704-binary-search", finding_messages(findings))

    def test_source_manifest_rejects_duplicate_leetcode_source_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "neetcode-all.json",
                {
                    "collectionId": "neetcode-all",
                    "sourceStatus": "pinned",
                    "sourceUrl": "https://neetcode.io/practice",
                    "expectedCount": 2,
                    "items": [
                        {
                            "sourceId": "2633",
                            "title": "Convert Object to JSON String",
                            "titleSlug": "convert-object-to-json-string",
                            "sourceUrl": "https://leetcode.com/problems/convert-object-to-json-string",
                            "collectionId": "neetcode-all",
                            "group": "JavaScript",
                            "order": 1,
                            "difficulty": "medium",
                            "dedupeKey": "leetcode:2633:convert-object-to-json-string",
                            "canonicalId": "lc-2633-convert-object-to-json-string",
                        },
                        {
                            "sourceId": "2633",
                            "title": "Neighboring Bitwise XOR",
                            "titleSlug": "neighboring-bitwise-xor",
                            "sourceUrl": "https://leetcode.com/problems/neighboring-bitwise-xor",
                            "collectionId": "neetcode-all",
                            "group": "Bit Manipulation",
                            "order": 2,
                            "difficulty": "medium",
                            "dedupeKey": "leetcode:2633:neighboring-bitwise-xor",
                            "canonicalId": "lc-2633-neighboring-bitwise-xor",
                        },
                    ],
                },
            )

            findings = validate_source_manifests(load_source_manifests(root))

            self.assertIn("duplicate sourceId 2633", finding_messages(findings))

    def test_source_manifest_rejects_unsafe_collection_id_and_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "bad.json",
                {
                    "collectionId": "../bad",
                    "sourceStatus": "pinned",
                    "sourceUrl": "http://example.com/list",
                    "expectedCount": 0,
                    "items": [],
                },
            )

            findings = validate_source_manifests(load_source_manifests(root))
            messages = finding_messages(findings)

            self.assertIn("collectionId ../bad is not a safe slug", messages)
            self.assertIn("sourceUrl must use https and an allowed host", messages)

    def test_blocked_unpinned_neetcode_manifest_is_non_strict_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "neetcode-all.json",
                {
                    "collectionId": "neetcode-all",
                    "sourceStatus": "blocked-source-unpinned",
                    "sourceUrl": "https://neetcode.io/practice",
                    "expectedCount": None,
                    "items": [],
                },
            )

            findings = validate_source_manifests(load_source_manifests(root), strict=False)

            self.assertEqual("warning", findings[0].severity)
            self.assertIn("source snapshot is not pinned", findings[0].message)

    def test_blocked_unpinned_neetcode_manifest_is_error_in_strict_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "neetcode-all.json",
                {
                    "collectionId": "neetcode-all",
                    "sourceStatus": "blocked-source-unpinned",
                    "sourceUrl": "https://neetcode.io/practice",
                    "expectedCount": None,
                    "items": [],
                },
            )

            findings = validate_source_manifests(load_source_manifests(root), strict=True)

            self.assertEqual("error", findings[0].severity)
            self.assertIn("source snapshot is not pinned", findings[0].message)


class DriverValidationTest(unittest.TestCase):
    def test_java_major_version_parses_legacy_and_modern_outputs(self) -> None:
        self.assertEqual(8, java_major_version('java version "1.8.0_491"'))
        self.assertEqual(11, java_major_version('javac 11.0.22'))
        self.assertEqual(17, java_major_version('openjdk version "17.0.10" 2024-01-16'))
        self.assertEqual(21, java_major_version('javac 21'))
        self.assertIsNone(java_major_version("not a version"))

    def test_all_problem_java_driver_cli_preflights_toolchain_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as fake_bin:
            root = Path(tmp)
            (root / "05-coding-problems" / "problem-bank").mkdir(parents=True)
            fake_java = Path(fake_bin) / "java"
            fake_java.write_text(
                "#!/bin/sh\n"
                "echo 'java version \"1.8.0_491\"' >&2\n"
                "exit 0\n",
                encoding="utf-8",
            )
            fake_java.chmod(0o755)
            fake_javac = Path(fake_bin) / "javac"
            fake_javac.write_text(
                "#!/bin/sh\n"
                "echo 'javac 1.8.0_491'\n"
                "exit 0\n",
                encoding="utf-8",
            )
            fake_javac.chmod(0o755)

            result = run_python_command(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "check_coding_problem_catalog.py"),
                    "--drivers",
                    "--allow-unsafe-driver-execution",
                    "--language",
                    "java",
                    "--root",
                    str(root),
                ],
                REPO_ROOT,
                env={"PATH": fake_bin + os.pathsep + os.environ.get("PATH", "")},
            )

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertEqual(1, result.stdout.count("ERROR "))
            self.assertIn("Java toolchain must be Java 11+", result.stdout)

    def test_driver_api_requires_unsafe_execution_acknowledgement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid_problem(root)

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python")

            self.assertIn(
                "driver execution requires allow_unsafe_driver_execution=True",
                finding_messages(findings),
            )

    def test_driver_cli_requires_unsafe_execution_acknowledgement(self) -> None:
        result = run_python_command(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "check_coding_problem_catalog.py"),
                "--drivers",
                "--language",
                "python",
                "--problem",
                "lc-0001-two-sum",
            ],
            REPO_ROOT,
        )

        self.assertEqual(2, result.returncode)
        self.assertIn("--drivers requires --allow-unsafe-driver-execution", result.stderr)

    def test_driver_generation_check_does_not_require_unsafe_execution(self) -> None:
        result = run_python_command(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "check_coding_problem_catalog.py"),
                "--driver-generation",
                "--problem",
                "lc-0088-merge-sorted-array",
            ],
            REPO_ROOT,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("PASS driver generation 1 problem(s)", result.stdout)

    def test_driver_generation_rejects_unsafe_signature_identifiers_before_source_interpolation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"]["methodName"] = "twoSum);"
            problem_payload["signature"]["java"]["parameters"][0]["name"] = "nums;"
            write_json(problem / "problem.json", problem_payload)

            findings, count = validate_driver_generation(root, "lc-0001-two-sum")
            messages = finding_messages(findings)

            self.assertEqual(1, count)
            self.assertIn("signature.java.methodName must be a safe identifier", messages)
            self.assertIn("signature.java.parameters name must be a safe identifier", messages)

    def test_python_driver_runs_solution_tier(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def twoSum(self, nums: List[int], target: int) -> List[int]:\n"
                "        for i in range(len(nums)):\n"
                "            for j in range(i + 1, len(nums)):\n"
                "                if nums[i] + nums[j] == target:\n"
                "                    return [i, j]\n"
                "        return []\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_imports_temp_copy_without_source_bytecode_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            solution_path = Path(tmp) / "problem" / "python" / "solution-1" / "solution.py"
            write_text(
                solution_path,
                "class Solution:\n"
                "    def echo(self, nums):\n"
                "        return nums\n",
            )

            findings = run_python_solution_subprocess(
                solution_path,
                {
                    "className": "Solution",
                    "methodName": "echo",
                    "returnType": "List[int]",
                    "parameters": [{"name": "nums", "type": "List[int]"}],
                    "cases": {
                        "matcher": {"type": "exact"},
                        "cases": [
                            {
                                "name": "identity",
                                "input": {"nums": [1, 2, 3]},
                                "expected": [1, 2, 3],
                            }
                        ],
                    },
                },
            )

            self.assertEqual([], findings, finding_messages(findings))
            self.assertFalse((solution_path.parent / "__pycache__").exists())

    def test_python_driver_reports_missing_callable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    pass\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("missing callable twoSum", finding_messages(findings))

    def test_python_driver_runs_in_child_process(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "import os\n"
                "from typing import List\n"
                "class Solution:\n"
                "    def twoSum(self, nums: List[int], target: int) -> List[int]:\n"
                "        os._exit(7)\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("Python driver exited with status 7", finding_messages(findings))

    def test_python_driver_rejects_zero_case_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            cases_payload = json.loads((problem / "cases.json").read_text(encoding="utf-8"))
            cases_payload["cases"] = []
            write_json(problem / "cases.json", cases_payload)

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("driver requires at least one test case", finding_messages(findings))

    def test_java_driver_source_supports_string_and_boolean_cases(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "canConstruct",
                "returnType": "boolean",
                "parameters": [
                    {"name": "ransomNote", "type": "String"},
                    {"name": "magazine", "type": "String"},
                ],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "enough letters",
                        "input": {"ransomNote": "moon", "magazine": "onomatopoeia"},
                        "expected": True,
                    }
                ],
            },
        )

        self.assertIn('String case1_ransomNote = "moon";', source)
        self.assertIn('boolean case1_actual = solution.canConstruct', source)
        self.assertIn("if (case1_actual != true)", source)

    def test_java_driver_source_supports_escaped_strings_false_and_string_returns(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "normalize",
                "returnType": "String",
                "parameters": [{ "name": "value", "type": "String" }],
            },
            {
                "matcher": { "type": "exact" },
                "cases": [
                    {
                        "name": "escaped",
                        "input": { "value": "a\"b" },
                        "expected": "ab",
                    }
                ],
            },
        )

        self.assertIn('String case1_value = "a\\"b";', source)
        self.assertIn('String case1_actual = solution.normalize', source)
        self.assertIn('Objects.equals(case1_actual, "ab")', source)

    def test_java_driver_source_supports_string_arrays_and_nested_int_arrays(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "merge",
                "returnType": "int[][]",
                "parameters": [
                    {"name": "intervals", "type": "int[][]"},
                    {"name": "labels", "type": "String[]"},
                ],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "nested",
                        "input": {
                            "intervals": [[1, 3], [2, 6]],
                            "labels": ["a", "b"],
                        },
                        "expected": [[1, 6]],
                    }
                ],
            },
        )

        self.assertIn("int[][] case1_intervals = new int[][] {new int[] {1, 3}, new int[] {2, 6}};", source)
        self.assertIn('String[] case1_labels = new String[] {"a", "b"};', source)
        self.assertIn("int[][] case1_actual = solution.merge", source)
        self.assertIn("Arrays.deepEquals(case1_actual, new int[][] {new int[] {1, 6}})", source)

    def test_java_driver_source_supports_string_array_return(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "tokens",
                "returnType": "String[]",
                "parameters": [{"name": "value", "type": "String"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "split",
                        "input": {"value": "a b"},
                        "expected": ["a", "b"],
                    }
                ],
            },
        )

        self.assertIn('String[] case1_actual = solution.tokens', source)
        self.assertIn('Arrays.equals(case1_actual, new String[] {"a", "b"})', source)

    def test_java_driver_source_supports_official_list_return_types(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "threeSum",
                "returnType": "List<List<Integer>>",
                "parameters": [{"name": "nums", "type": "int[]"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "two triplets",
                        "input": {"nums": [-2, -1, 0, 1, 2]},
                        "expected": [[-2, 0, 2], [-1, 0, 1]],
                    }
                ],
            },
        )

        self.assertIn("List<List<Integer>> case1_actual = solution.threeSum", source)
        self.assertIn(
            "Objects.equals(case1_actual, Arrays.asList(Arrays.asList(-2, 0, 2), Arrays.asList(-1, 0, 1)))",
            source,
        )

    def test_java_driver_source_supports_official_list_parameter_types(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "inspect",
                "returnType": "int",
                "parameters": [
                    {"name": "wordDict", "type": "List<String>"},
                    {"name": "costs", "type": "List<Integer>"},
                    {"name": "weights", "type": "List<Double>"},
                    {"name": "triangle", "type": "List<List<Integer>>"},
                ],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "list params",
                        "input": {
                            "wordDict": ["leet", "code"],
                            "costs": [1, 2, 3],
                            "weights": [1.25, -2.5],
                            "triangle": [[2], [3, 4]],
                        },
                        "expected": 6,
                    }
                ],
            },
        )

        self.assertIn('List<String> case1_wordDict = Arrays.asList("leet", "code");', source)
        self.assertIn("List<Integer> case1_costs = Arrays.asList(1, 2, 3);", source)
        self.assertIn("List<Double> case1_weights = Arrays.asList(1.25d, -2.5d);", source)
        self.assertIn("List<List<Integer>> case1_triangle = Arrays.asList(Arrays.asList(2), Arrays.asList(3, 4));", source)
        self.assertIn("int case1_actual = solution.inspect(case1_wordDict, case1_costs, case1_weights, case1_triangle);", source)

    def test_java_driver_source_supports_double_and_list_double_with_tolerance(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "averages",
                "returnType": "List<Double>",
                "parameters": [{"name": "x", "type": "double"}],
            },
            {
                "matcher": {"type": "float-tolerance", "tolerance": 0.000001},
                "cases": [
                    {
                        "name": "double list",
                        "input": {"x": -2.5},
                        "expected": [-2.5, 0.0],
                    }
                ],
            },
        )

        self.assertIn("double case1_x = -2.5d;", source)
        self.assertIn("List<Double> case1_actual = solution.averages(case1_x);", source)
        self.assertIn("floatListEquals(case1_actual, Arrays.asList(-2.5d, 0.0d), 1e-06d)", source)

    def test_java_driver_source_supports_object_operations(self) -> None:
        source = java_driver_source(
            {
                "kind": "object",
                "className": "MinStack",
                "constructor": {"parameters": []},
                "methods": [
                    {"name": "push", "returnType": "void", "parameters": [{"name": "val", "type": "int"}]},
                    {"name": "getMin", "returnType": "int", "parameters": []},
                ],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "basic stack",
                        "operations": [
                            {"type": "constructor", "input": {}, "expected": None},
                            {"type": "call", "method": "push", "input": {"val": 4}, "expected": None},
                            {"type": "call", "method": "getMin", "input": {}, "expected": 4},
                        ],
                    }
                ],
            },
        )

        self.assertIn("MinStack case1_instance = new MinStack();", source)
        self.assertIn("case1_instance.push(4);", source)
        self.assertIn("int case1_op3_actual = case1_instance.getMin();", source)
        self.assertIn("if (case1_op3_actual != 4)", source)

    def test_java_driver_source_supports_object_char_returns(self) -> None:
        source = java_driver_source(
            {
                "kind": "object",
                "className": "StringIterator",
                "constructor": {"parameters": [{"name": "compressedString", "type": "String"}]},
                "methods": [{"name": "next", "returnType": "char", "parameters": []}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "characters and exhausted sentinel",
                        "operations": [
                            {"type": "constructor", "input": {"compressedString": "a1"}, "expected": None},
                            {"type": "call", "method": "next", "input": {}, "expected": "a"},
                            {"type": "call", "method": "next", "input": {}, "expected": " "},
                        ],
                    }
                ],
            },
        )

        self.assertIn('StringIterator case1_instance = new StringIterator("a1");', source)
        self.assertIn("char case1_op2_actual = case1_instance.next();", source)
        self.assertIn("if (case1_op2_actual != 'a')", source)
        self.assertIn("if (case1_op3_actual != ' ')", source)

    def test_java_driver_source_supports_unordered_string_nested_list_matcher(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "groupAnagrams",
                "returnType": "List<List<String>>",
                "parameters": [{"name": "strs", "type": "String[]"}],
            },
            {
                "matcher": {"type": "unordered-list-of-lists"},
                "cases": [
                    {
                        "name": "same groups different order",
                        "input": {"strs": ["arc", "car", "rat"]},
                        "expected": [["arc", "car"], ["rat"]],
                    }
                ],
            },
        )

        self.assertIn(
            'unorderedListOfListsEquals(case1_actual, Arrays.asList(Arrays.asList("arc", "car"), Arrays.asList("rat")))',
            source,
        )
        self.assertIn("private static boolean unorderedListOfListsEquals(List<? extends List<?>> actual, List<? extends List<?>> expected)", source)
        self.assertIn("item instanceof String", source)

    def test_java_driver_source_supports_unordered_int_matrix_matcher(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "kClosest",
                "returnType": "int[][]",
                "parameters": [{"name": "points", "type": "int[][]"}, {"name": "k", "type": "int"}],
            },
            {
                "matcher": {"type": "unordered-list-of-lists"},
                "cases": [
                    {
                        "name": "same points different order",
                        "input": {"points": [[3, 4], [1, 1], [2, 2]], "k": 2},
                        "expected": [[1, 1], [2, 2]],
                    }
                ],
            },
        )

        self.assertIn(
            "unorderedIntMatrixEquals(case1_actual, new int[][] {new int[] {1, 1}, new int[] {2, 2}})",
            source,
        )
        self.assertIn("private static boolean unorderedIntMatrixEquals(int[][] actual, int[][] expected)", source)

    def test_java_driver_literals_reject_bool_for_integer_shapes(self) -> None:
        for signature, cases in (
            (
                {
                    "className": "Solution",
                    "methodName": "echo",
                    "returnType": "int[]",
                    "parameters": [{"name": "nums", "type": "int[]"}],
                },
                {
                    "matcher": {"type": "exact"},
                    "cases": [{"name": "bool", "input": {"nums": [True, 2]}, "expected": [1, 2]}],
                },
            ),
            (
                {
                    "className": "Solution",
                    "methodName": "values",
                    "returnType": "List<Integer>",
                    "parameters": [{"name": "nums", "type": "int[]"}],
                },
                {
                    "matcher": {"type": "exact"},
                    "cases": [{"name": "bool", "input": {"nums": [1]}, "expected": [True]}],
                },
            ),
        ):
            with self.subTest(return_type=signature["returnType"]):
                with self.assertRaises(ValueError):
                    java_driver_source(signature, cases)

    def test_java_driver_source_supports_char_grid_inputs(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "exist",
                "returnType": "boolean",
                "parameters": [
                    {"name": "board", "type": "char[][]"},
                    {"name": "word", "type": "String"},
                ],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "word present",
                        "input": {"board": [["A", "B"], ["C", "D"]], "word": "AB"},
                        "expected": True,
                    }
                ],
            },
        )

        self.assertIn("char[][] case1_board = new char[][] {new char[] {'A', 'B'}, new char[] {'C', 'D'}};", source)
        self.assertIn('String case1_word = "AB";', source)
        self.assertIn("boolean case1_actual = solution.exist", source)

    def test_java_driver_source_supports_char_grid_mutation_cases(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "solve",
                "returnType": "void",
                "parameters": [{"name": "board", "type": "char[][]"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "capture center",
                        "input": {"board": [["X", "X", "X"], ["X", "O", "X"], ["X", "X", "X"]]},
                        "expected": None,
                        "expectedMutations": {"board": [["X", "X", "X"], ["X", "X", "X"], ["X", "X", "X"]]},
                    }
                ],
            },
        )

        self.assertIn("solution.solve(case1_board);", source)
        self.assertIn("Arrays.deepEquals(case1_board, new char[][]", source)

    def test_java_driver_source_supports_void_mutation_cases(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "merge",
                "returnType": "void",
                "parameters": [
                    {"name": "nums1", "type": "int[]"},
                    {"name": "m", "type": "int"},
                    {"name": "nums2", "type": "int[]"},
                    {"name": "n", "type": "int"},
                ],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "merge into buffer",
                        "input": {"nums1": [2, 5, 0, 0], "m": 2, "nums2": [1, 6], "n": 2},
                        "expected": None,
                        "expectedMutations": {"nums1": [1, 2, 5, 6]},
                    }
                ],
            },
        )

        self.assertIn("solution.merge(case1_nums1, case1_m, case1_nums2, case1_n);", source)
        self.assertNotIn("void case1_actual", source)
        self.assertIn("Arrays.equals(case1_nums1, new int[] {1, 2, 5, 6})", source)

    def test_java_driver_source_supports_list_node_mutation_cases(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "reorderList",
                "returnType": "void",
                "parameters": [{"name": "head", "type": "ListNode"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "reorder compact chain",
                        "input": {"head": [1, 2, 3, 4]},
                        "expected": None,
                        "expectedMutations": {"head": [1, 4, 2, 3]},
                        "linkedListContract": {"postCall": {"head": [0, 3, 1, 2]}},
                    }
                ],
            },
        )

        self.assertIn("solution.reorderList(case1_head);", source)
        self.assertIn("listEquals(case1_head, new int[] {1, 4, 2, 3})", source)
        self.assertIn("listIdentityEquals(case1_head, case1_head_nodes, new int[] {0, 3, 1, 2})", source)

    def test_java_driver_source_supports_prefix_mutation_cases(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "removeElement",
                "returnType": "int",
                "parameters": [
                    {"name": "nums", "type": "int[]"},
                    {"name": "val", "type": "int"},
                ],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "remove matching value",
                        "input": {"nums": [3, 1, 3, 2], "val": 3},
                        "expected": 2,
                        "expectedMutations": {"nums": {"prefix": [1, 2], "lengthFrom": "return"}},
                    }
                ],
            },
        )

        self.assertIn("int case1_actual = solution.removeElement(case1_nums, case1_val);", source)
        self.assertIn("Arrays.copyOf(case1_nums, case1_actual)", source)
        self.assertIn("new int[] {1, 2}", source)

    def test_java_driver_source_supports_list_node_cases(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "ListNode",
                "parameters": [{"name": "head", "type": "ListNode"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "reverse compact chain",
                        "input": {"head": [4, 1, 9]},
                        "expected": [9, 1, 4],
                        "linkedListContract": {
                            "result": {"from": "head", "nodeIndices": [2, 1, 0]}
                        },
                    },
                    {
                        "name": "empty chain",
                        "input": {"head": None},
                        "expected": None,
                    },
                ],
            },
        )

        self.assertIn("class ListNode", source)
        self.assertIn("ListNode case1_head = buildList(new int[] {4, 1, 9});", source)
        self.assertIn("ListNode[] case1_head_nodes = listNodes(case1_head);", source)
        self.assertIn("ListNode case1_actual = solution.reverseList(case1_head);", source)
        self.assertIn("listEquals(case1_actual, new int[] {9, 1, 4})", source)
        self.assertIn("listIdentityEquals(case1_actual, case1_head_nodes, new int[] {2, 1, 0})", source)
        self.assertIn("ListNode case2_head = null;", source)
        self.assertIn("if (case2_actual != null)", source)

        palindrome_source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "isPalindrome",
                "returnType": "boolean",
                "parameters": [{"name": "head", "type": "ListNode"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "mismatch preserves input",
                        "input": {"head": [9, 1, 9, 2]},
                        "expected": False,
                        "linkedListContract": {"postCall": {"head": [0, 1, 2, 3]}},
                    }
                ],
            },
        )

        self.assertIn("boolean case1_actual = solution.isPalindrome(case1_head);", palindrome_source)
        self.assertIn("ListNode[] case1_head_nodes = listNodes(case1_head);", palindrome_source)
        self.assertIn("listIdentityEquals(case1_head, case1_head_nodes, new int[] {0, 1, 2, 3})", palindrome_source)

    def test_java_driver_source_supports_cyclic_list_node_input(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "hasCycle",
                "returnType": "boolean",
                "parameters": [{"name": "head", "type": "ListNode"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "cycle to middle",
                        "input": {"head": {"values": [6, 1, 8, 5], "cycleTo": 2}},
                        "expected": True,
                    }
                ],
            },
        )

        self.assertIn("private static ListNode buildCyclicList(int[] values, int cycleTo)", source)
        self.assertIn("ListNode case1_head = buildCyclicList(new int[] {6, 1, 8, 5}, 2);", source)
        self.assertIn("boolean case1_actual = solution.hasCycle(case1_head);", source)
        self.assertNotIn("ListNode[] case1_head_nodes", source)

    def test_java_driver_source_rejects_malformed_cyclic_list_node_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected cyclic ListNode values and valid cycleTo index"):
            java_driver_source(
                {
                    "className": "Solution",
                    "methodName": "hasCycle",
                    "returnType": "boolean",
                    "parameters": [{"name": "head", "type": "ListNode"}],
                },
                {
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "bad cycle",
                            "input": {"head": {"values": [], "cycleTo": 0}},
                            "expected": False,
                        }
                    ],
                },
            )

    def test_java_driver_source_supports_list_node_array_parameters(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "mergeKLists",
                "returnType": "ListNode",
                "parameters": [{"name": "lists", "type": "ListNode[]"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "three chains",
                        "input": {"lists": [[1, 4], None, [2, 3]]},
                        "expected": [1, 2, 3, 4],
                    }
                ],
            },
        )

        self.assertIn("class ListNode", source)
        self.assertIn(
            "ListNode[] case1_lists = new ListNode[] {buildList(new int[] {1, 4}), null, buildList(new int[] {2, 3})};",
            source,
        )
        self.assertIn("ListNode case1_actual = solution.mergeKLists(case1_lists);", source)
        self.assertIn("listEquals(case1_actual, new int[] {1, 2, 3, 4})", source)

    def test_java_driver_source_supports_tree_node_cases(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "invertTree",
                "returnType": "TreeNode",
                "parameters": [{"name": "root", "type": "TreeNode"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "balanced tree",
                        "input": {"root": [8, 4, 12, 2, 6, 10, 14]},
                        "expected": [8, 12, 4, 14, 10, 6, 2],
                    },
                    {
                        "name": "missing left branch",
                        "input": {"root": [5, None, 8]},
                        "expected": [5, 8],
                    },
                ],
            },
        )

        self.assertIn("class TreeNode", source)
        self.assertIn("TreeNode case1_root = buildTree(new Integer[] {8, 4, 12, 2, 6, 10, 14});", source)
        self.assertIn("TreeNode case1_actual = solution.invertTree(case1_root);", source)
        self.assertIn("Objects.equals(treeValues(case1_actual), Arrays.asList(8, 12, 4, 14, 10, 6, 2))", source)
        self.assertIn("TreeNode case2_root = buildTree(new Integer[] {5, null, 8});", source)

    def test_java_driver_source_supports_unordered_tree_list_matcher(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "generateTrees",
                "returnType": "List<TreeNode>",
                "parameters": [{"name": "n", "type": "int"}],
            },
            {
                "matcher": {"type": "unordered-tree-list"},
                "cases": [
                    {
                        "name": "two possible roots",
                        "input": {"n": 2},
                        "expected": [[1, None, 2], [2, 1]],
                    }
                ],
            },
        )

        self.assertIn("class TreeNode", source)
        self.assertIn("List<TreeNode> case1_actual = solution.generateTrees(case1_n);", source)
        self.assertIn("unorderedTreeListEquals(case1_actual, Arrays.asList(buildTree(new Integer[] {1, null, 2}), buildTree(new Integer[] {2, 1})))", source)

    def test_java_driver_source_supports_tree_node_identity_references(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "TreeNode",
                "parameters": [
                    {"name": "root", "type": "TreeNode"},
                    {"name": "p", "type": "TreeNode"},
                    {"name": "q", "type": "TreeNode"},
                ],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "identity lca",
                        "input": {
                            "root": [9, 4, 13, 2, 6, 11, 15, None, 3, 5, 7],
                            "p": {"from": "root", "path": "LLR"},
                            "q": {"from": "root", "path": "LRL"},
                        },
                        "expected": {"from": "root", "path": "L"},
                    }
                ],
            },
        )

        self.assertIn("private static TreeNode treeNodeAtPath(TreeNode root, String path)", source)
        self.assertIn('TreeNode case1_p = treeNodeAtPath(case1_root, "LLR");', source)
        self.assertIn('TreeNode case1_q = treeNodeAtPath(case1_root, "LRL");', source)
        self.assertIn('TreeNode case1_expected = treeNodeAtPath(case1_root, "L");', source)
        self.assertIn("if (case1_actual != case1_expected)", source)

    def test_java_driver_source_supports_binary_tree_next_node_cases(self) -> None:
        source = java_driver_source(
            {
                "customTypes": {"Node": "binary-tree-next"},
                "className": "Solution",
                "methodName": "connect",
                "returnType": "Node",
                "parameters": [{"name": "root", "type": "Node"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "ragged next levels",
                        "input": {"root": [1, 2, 3, None, 4, None, 5]},
                        "expected": [[1], [2, 3], [4, 5]],
                        "expectedMutations": {"root": [[1], [2, 3], [4, 5]]},
                    }
                ],
            },
        )

        self.assertIn("class Node", source)
        self.assertIn("Node case1_root = buildNodeTree(new Integer[] {1, 2, 3, null, 4, null, 5});", source)
        self.assertIn("Node case1_actual = solution.connect(case1_root);", source)
        self.assertIn("Objects.equals(nodeNextLevels(case1_actual), Arrays.asList(Arrays.asList(1), Arrays.asList(2, 3), Arrays.asList(4, 5)))", source)
        self.assertIn("Objects.equals(nodeNextLevels(case1_root), Arrays.asList(Arrays.asList(1), Arrays.asList(2, 3), Arrays.asList(4, 5)))", source)

    def test_java_driver_source_supports_random_list_node_cases(self) -> None:
        source = java_driver_source(
            {
                "customTypes": {"Node": "random-list"},
                "className": "Solution",
                "methodName": "copyRandomList",
                "returnType": "Node",
                "parameters": [{"name": "head", "type": "Node"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "random pointers by index",
                        "input": {"head": [[8, None], [12, 0], [5, 2]]},
                        "expected": [[8, None], [12, 0], [5, 2]],
                    }
                ],
            },
        )

        self.assertIn("class Node", source)
        self.assertIn("Node case1_head = buildRandomList(new int[] {8, 12, 5}, new int[] {-1, 0, 2});", source)
        self.assertIn("Node[] case1_head_nodes = randomListNodes(case1_head);", source)
        self.assertIn("Node case1_actual = solution.copyRandomList(case1_head);", source)
        self.assertIn("Objects.equals(randomListValues(case1_actual, case1_head_nodes), Arrays.asList(Arrays.asList(8, null), Arrays.asList(12, 0), Arrays.asList(5, 2)))", source)

    def test_java_driver_source_supports_graph_node_cases(self) -> None:
        source = java_driver_source(
            {
                "customTypes": {"Node": "graph"},
                "className": "Solution",
                "methodName": "cloneGraph",
                "returnType": "Node",
                "parameters": [{"name": "node", "type": "Node"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "triangle",
                        "input": {"node": [[2, 3], [1, 3], [1, 2]]},
                        "expected": [[2, 3], [1, 3], [1, 2]],
                    }
                ],
            },
        )

        self.assertIn("class Node", source)
        self.assertIn("Node case1_node = buildGraph(new int[][] {new int[] {2, 3}, new int[] {1, 3}, new int[] {1, 2}});", source)
        self.assertIn("Node[] case1_node_nodes = graphNodes(case1_node);", source)
        self.assertIn("Node case1_actual = solution.cloneGraph(case1_node);", source)
        self.assertIn("Objects.equals(graphAdjacencyValues(case1_actual, case1_node_nodes), Arrays.asList(Arrays.asList(2, 3), Arrays.asList(1, 3), Arrays.asList(1, 2)))", source)

    def test_java_driver_source_supports_quad_tree_node_cases(self) -> None:
        expected = {
            "val": True,
            "isLeaf": False,
            "topLeft": {"val": True, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
            "topRight": {"val": False, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
            "bottomLeft": {"val": False, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
            "bottomRight": {"val": True, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
        }
        source = java_driver_source(
            {
                "customTypes": {"Node": "quad-tree"},
                "className": "Solution",
                "methodName": "construct",
                "returnType": "Node",
                "parameters": [{"name": "grid", "type": "int[][]"}],
            },
            {
                "matcher": {"type": "exact"},
                "cases": [
                    {
                        "name": "mixed quadrants",
                        "input": {"grid": [[1, 0], [0, 1]]},
                        "expected": expected,
                    }
                ],
            },
        )

        self.assertIn("class Node", source)
        self.assertIn("int[][] case1_grid = new int[][] {new int[] {1, 0}, new int[] {0, 1}};", source)
        self.assertIn("Node case1_actual = solution.construct(case1_grid);", source)
        self.assertIn("Objects.equals(quadTreeSignature(case1_actual)", source)

    def test_java_driver_source_supports_balanced_bst_matcher(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "sortedArrayToBST",
                "returnType": "TreeNode",
                "parameters": [{"name": "nums", "type": "int[]"}],
            },
            {
                "matcher": {"type": "balanced-bst-from-sorted-array"},
                "cases": [
                    {
                        "name": "semantic tree match",
                        "input": {"nums": [2, 5, 9, 12]},
                        "expected": [5, 2, 9, None, None, None, 12],
                    }
                ],
            },
        )

        self.assertIn("balancedBstMatchesSortedArray(case1_actual, case1_nums)", source)
        self.assertIn("private static boolean balancedBstMatchesSortedArray(TreeNode root, int[] nums)", source)

    def test_java_driver_source_supports_unordered_nested_list_matcher(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "permute",
                "returnType": "List<List<Integer>>",
                "parameters": [{"name": "nums", "type": "int[]"}],
            },
            {
                "matcher": {"type": "unordered-list-of-lists"},
                "cases": [
                    {
                        "name": "same rows different order",
                        "input": {"nums": [2, 4]},
                        "expected": [[2, 4], [4, 2]],
                    }
                ],
            },
        )

        self.assertIn("unorderedListOfListsEquals(case1_actual, Arrays.asList(Arrays.asList(2, 4), Arrays.asList(4, 2)))", source)
        self.assertIn("private static boolean unorderedListOfListsEquals(List<? extends List<?>> actual, List<? extends List<?>> expected)", source)
        self.assertIn("item instanceof Integer", source)

    def test_java_driver_source_supports_unordered_flat_list_matcher(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "letterCombinations",
                "returnType": "List<String>",
                "parameters": [{"name": "digits", "type": "String"}],
            },
            {
                "matcher": {"type": "unordered-list"},
                "cases": [
                    {
                        "name": "same rows different order",
                        "input": {"digits": "8"},
                        "expected": ["t", "u", "v"],
                    }
                ],
            },
        )

        self.assertIn("unorderedFlatListEquals(case1_actual, Arrays.asList(\"t\", \"u\", \"v\"))", source)
        self.assertIn("private static <T> boolean unorderedFlatListEquals(List<T> actual, List<T> expected)", source)

    def test_java_driver_source_supports_valid_topological_order_matcher(self) -> None:
        source = java_driver_source(
            {
                "className": "Solution",
                "methodName": "findOrder",
                "returnType": "int[]",
                "parameters": [
                    {"name": "numCourses", "type": "int"},
                    {"name": "prerequisites", "type": "int[][]"},
                ],
            },
            {
                "matcher": {"type": "valid-topological-order"},
                "cases": [
                    {
                        "name": "ambiguous order",
                        "input": {"numCourses": 4, "prerequisites": [[1, 0], [2, 0], [3, 1], [3, 2]]},
                        "expected": [0, 1, 2, 3],
                    }
                ],
            },
        )

        self.assertIn("validTopologicalOrder(case1_actual, case1_numCourses, case1_prerequisites)", source)
        self.assertIn("private static boolean validTopologicalOrder(int[] actual, int numCourses, int[][] prerequisites)", source)

    def test_python_driver_supports_none_return_and_mutation_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "merge",
                "returnType": "void",
                "parameters": [
                    {"name": "nums1", "type": "int[]"},
                    {"name": "m", "type": "int"},
                    {"name": "nums2", "type": "int[]"},
                    {"name": "n", "type": "int"},
                ],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "merge",
                "returnType": "None",
                "parameters": [
                    {"name": "nums1", "type": "List[int]"},
                    {"name": "m", "type": "int"},
                    {"name": "nums2", "type": "List[int]"},
                    {"name": "n", "type": "int"},
                ],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "merge into first buffer",
                            "input": {"nums1": [2, 5, 0, 0], "m": 2, "nums2": [1, 6], "n": 2},
                            "expected": None,
                            "expectedMutations": {"nums1": [1, 2, 5, 6]},
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:\n"
                "        merged = sorted(nums1[:m] + nums2[:n])\n"
                "        nums1[:] = merged\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_list_node_mutation_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "reorderList",
                "returnType": "void",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "reorderList",
                "returnType": "None",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "reorder compact chain",
                            "input": {"head": [1, 2, 3, 4]},
                            "expected": None,
                            "expectedMutations": {"head": [1, 4, 2, 3]},
                            "linkedListContract": {"postCall": {"head": [0, 3, 1, 2]}},
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import Optional\n\n"
                "class Solution:\n"
                "    def reorderList(self, head: Optional[ListNode]) -> None:\n"
                "        nodes = []\n"
                "        current = head\n"
                "        while current:\n"
                "            nodes.append(current)\n"
                "            current = current.next\n"
                "        order = []\n"
                "        left = 0\n"
                "        right = len(nodes) - 1\n"
                "        while left <= right:\n"
                "            order.append(nodes[left])\n"
                "            if left != right:\n"
                "                order.append(nodes[right])\n"
                "            left += 1\n"
                "            right -= 1\n"
                "        for index in range(len(order) - 1):\n"
                "            order[index].next = order[index + 1]\n"
                "        if order:\n"
                "            order[-1].next = None\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_list_node_inputs_and_returns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "ListNode",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "Optional[ListNode]",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "reverse compact chain",
                            "input": {"head": [4, 1, 9]},
                            "expected": [9, 1, 4],
                            "linkedListContract": {
                                "result": {"from": "head", "nodeIndices": [2, 1, 0]}
                            },
                        },
                        {
                            "name": "empty chain",
                            "input": {"head": None},
                            "expected": None,
                        },
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:\n"
                "        previous = None\n"
                "        current = head\n"
                "        while current is not None:\n"
                "            following = current.next\n"
                "            current.next = previous\n"
                "            previous = current\n"
                "            current = following\n"
                "        return previous\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_cyclic_list_node_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "hasCycle",
                "returnType": "boolean",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "hasCycle",
                "returnType": "bool",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "cycle to middle",
                            "input": {"head": {"values": [6, 1, 8, 5], "cycleTo": 2}},
                            "expected": True,
                        },
                        {
                            "name": "acyclic chain",
                            "input": {"head": [1, 2, 3]},
                            "expected": False,
                        },
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def hasCycle(self, head: Optional[ListNode]) -> bool:\n"
                "        seen = set()\n"
                "        current = head\n"
                "        while current is not None:\n"
                "            marker = id(current)\n"
                "            if marker in seen:\n"
                "                return True\n"
                "            seen.add(marker)\n"
                "            current = current.next\n"
                "        return False\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_list_node_array_parameters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "mergeKLists",
                "returnType": "ListNode",
                "parameters": [{"name": "lists", "type": "ListNode[]"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "mergeKLists",
                "returnType": "Optional[ListNode]",
                "parameters": [{"name": "lists", "type": "List[Optional[ListNode]]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "three chains",
                            "input": {"lists": [[1, 4], None, [2, 3]]},
                            "expected": [1, 2, 3, 4],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:\n"
                "        values = []\n"
                "        for head in lists:\n"
                "            while head is not None:\n"
                "                values.append(head.val)\n"
                "                head = head.next\n"
                "        values.sort()\n"
                "        dummy = ListNode(0)\n"
                "        tail = dummy\n"
                "        for value in values:\n"
                "            tail.next = ListNode(value)\n"
                "            tail = tail.next\n"
                "        return dummy.next\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_tree_node_inputs_and_returns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "invertTree",
                "returnType": "TreeNode",
                "parameters": [{"name": "root", "type": "TreeNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "invertTree",
                "returnType": "Optional[TreeNode]",
                "parameters": [{"name": "root", "type": "Optional[TreeNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                    {
                        "name": "balanced tree",
                        "input": {"root": [8, 4, 12, 2, 6, 10, 14]},
                        "expected": [8, 12, 4, 14, 10, 6, 2],
                    },
                        {
                            "name": "empty tree",
                            "input": {"root": []},
                            "expected": [],
                        },
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:\n"
                "        if root is None:\n"
                "            return None\n"
                "        root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)\n"
                "        return root\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_tree_node_identity_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "TreeNode",
                "parameters": [
                    {"name": "root", "type": "TreeNode"},
                    {"name": "p", "type": "TreeNode"},
                    {"name": "q", "type": "TreeNode"},
                ],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "Optional[TreeNode]",
                "parameters": [
                    {"name": "root", "type": "Optional[TreeNode]"},
                    {"name": "p", "type": "Optional[TreeNode]"},
                    {"name": "q", "type": "Optional[TreeNode]"},
                ],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "identity lca",
                            "input": {
                                "root": [9, 4, 13, 2, 6, 11, 15, None, 3, 5, 7],
                                "p": {"from": "root", "path": "LLR"},
                                "q": {"from": "root", "path": "LRL"},
                            },
                            "expected": {"from": "root", "path": "L"},
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def lowestCommonAncestor(self, root: Optional[TreeNode], p: Optional[TreeNode], q: Optional[TreeNode]) -> Optional[TreeNode]:\n"
                "        if root is None or root is p or root is q:\n"
                "            return root\n"
                "        left = self.lowestCommonAncestor(root.left, p, q)\n"
                "        right = self.lowestCommonAncestor(root.right, p, q)\n"
                "        if left is not None and right is not None:\n"
                "            return root\n"
                "        return left if left is not None else right\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_rejects_rebuilt_tree_node_when_identity_reference_expected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "TreeNode",
                "parameters": [
                    {"name": "root", "type": "TreeNode"},
                    {"name": "p", "type": "TreeNode"},
                    {"name": "q", "type": "TreeNode"},
                ],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "Optional[TreeNode]",
                "parameters": [
                    {"name": "root", "type": "Optional[TreeNode]"},
                    {"name": "p", "type": "Optional[TreeNode]"},
                    {"name": "q", "type": "Optional[TreeNode]"},
                ],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "rebuilt node fails identity",
                            "input": {
                                "root": [9, 4, 13, 2, 6, 11, 15, None, 3, 5, 7],
                                "p": {"from": "root", "path": "LLR"},
                                "q": {"from": "root", "path": "LRL"},
                            },
                            "expected": {"from": "root", "path": "L"},
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def lowestCommonAncestor(self, root: Optional[TreeNode], p: Optional[TreeNode], q: Optional[TreeNode]) -> Optional[TreeNode]:\n"
                "        return TreeNode(4)\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("expected {'from': 'root', 'path': 'L'} got [4]", finding_messages(findings))

    def test_python_driver_supports_tree_node_mutation_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "flatten",
                "returnType": "void",
                "parameters": [{"name": "root", "type": "TreeNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "flatten",
                "returnType": "None",
                "parameters": [{"name": "root", "type": "Optional[TreeNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "flatten mutation",
                            "input": {"root": [1, 2, 3]},
                            "expected": None,
                            "expectedMutations": {"root": [1, None, 2, None, 3]},
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def flatten(self, root: Optional[TreeNode]) -> None:\n"
                "        values = []\n"
                "        def preorder(node: Optional[TreeNode]) -> None:\n"
                "            if node is None:\n"
                "                return\n"
                "            values.append(node)\n"
                "            preorder(node.left)\n"
                "            preorder(node.right)\n"
                "        preorder(root)\n"
                "        for index, node in enumerate(values):\n"
                "            node.left = None\n"
                "            node.right = values[index + 1] if index + 1 < len(values) else None\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_binary_tree_next_node_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "binary-tree-next"},
                "java": {
                    "className": "Solution",
                    "methodName": "connect",
                    "returnType": "Node",
                    "parameters": [{"name": "root", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "connect",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "root", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "ragged next levels",
                            "input": {"root": [1, 2, 3, None, 4, None, 5]},
                            "expected": [[1], [2, 3], [4, 5]],
                            "expectedMutations": {"root": [[1], [2, 3], [4, 5]]},
                        },
                        {
                            "name": "empty tree",
                            "input": {"root": []},
                            "expected": [],
                            "expectedMutations": {"root": []},
                        },
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def connect(self, root: Optional[Node]) -> Optional[Node]:\n"
                "        level = [root] if root is not None else []\n"
                "        while level:\n"
                "            next_level = []\n"
                "            previous = None\n"
                "            for node in level:\n"
                "                if previous is not None:\n"
                "                    previous.next = node\n"
                "                previous = node\n"
                "                if node.left is not None:\n"
                "                    next_level.append(node.left)\n"
                "                if node.right is not None:\n"
                "                    next_level.append(node.right)\n"
                "            if previous is not None:\n"
                "                previous.next = None\n"
                "            level = next_level\n"
                "        return root\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_random_list_node_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "random-list"},
                "java": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Node",
                    "parameters": [{"name": "head", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "head", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "random pointers by index",
                            "input": {"head": [[8, None], [12, 0], [5, 2]]},
                            "expected": [[8, None], [12, 0], [5, 2]],
                        },
                        {
                            "name": "empty list",
                            "input": {"head": []},
                            "expected": [],
                        },
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def copyRandomList(self, head: Optional[Node]) -> Optional[Node]:\n"
                "        if head is None:\n"
                "            return None\n"
                "        old_to_new = {}\n"
                "        current = head\n"
                "        while current is not None:\n"
                "            old_to_new[current] = Node(current.val)\n"
                "            current = current.next\n"
                "        current = head\n"
                "        while current is not None:\n"
                "            clone = old_to_new[current]\n"
                "            clone.next = old_to_new.get(current.next)\n"
                "            clone.random = old_to_new.get(current.random)\n"
                "            current = current.next\n"
                "        return old_to_new[head]\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_random_list_official_constructor_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "random-list"},
                "java": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Node",
                    "parameters": [{"name": "head", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "head", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "constructor keyword copy",
                            "input": {"head": [[8, None], [12, 0]]},
                            "expected": [[8, None], [12, 0]],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def copyRandomList(self, head: Optional[Node]) -> Optional[Node]:\n"
                "        if head is None:\n"
                "            return None\n"
                "        first = Node(head.val, random=None)\n"
                "        second = Node(head.next.val, next=None, random=first)\n"
                "        first.next = second\n"
                "        return first\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_rejects_random_list_reusing_input_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "random-list"},
                "java": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Node",
                    "parameters": [{"name": "head", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "head", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "identity reuse is invalid",
                            "input": {"head": [[4, None], [9, 0]]},
                            "expected": [[4, None], [9, 0]],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def copyRandomList(self, head: Optional[Node]) -> Optional[Node]:\n"
                "        return head\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("random-list Node output reuses an input node", finding_messages(findings))

    def test_python_driver_supports_graph_node_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "graph"},
                "java": {
                    "className": "Solution",
                    "methodName": "cloneGraph",
                    "returnType": "Node",
                    "parameters": [{"name": "node", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "cloneGraph",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "node", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "triangle",
                            "input": {"node": [[2, 3], [1, 3], [1, 2]]},
                            "expected": [[2, 3], [1, 3], [1, 2]],
                        },
                        {
                            "name": "empty graph",
                            "input": {"node": []},
                            "expected": [],
                        },
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def cloneGraph(self, node: Optional[Node]) -> Optional[Node]:\n"
                "        if node is None:\n"
                "            return None\n"
                "        clones = {}\n"
                "        def clone(current: Node) -> Node:\n"
                "            if current in clones:\n"
                "                return clones[current]\n"
                "            copied = Node(current.val)\n"
                "            clones[current] = copied\n"
                "            copied.neighbors = [clone(neighbor) for neighbor in current.neighbors]\n"
                "            return copied\n"
                "        return clone(node)\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_rejects_graph_reusing_input_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "graph"},
                "java": {
                    "className": "Solution",
                    "methodName": "cloneGraph",
                    "returnType": "Node",
                    "parameters": [{"name": "node", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "cloneGraph",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "node", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "identity reuse is invalid",
                            "input": {"node": [[2], [1]]},
                            "expected": [[2], [1]],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def cloneGraph(self, node: Optional[Node]) -> Optional[Node]:\n"
                "        return node\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("graph Node output reuses an input node", finding_messages(findings))

    def test_python_driver_supports_graph_node_mutation_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "graph"},
                "java": {
                    "className": "Solution",
                    "methodName": "preserveGraph",
                    "returnType": "Node",
                    "parameters": [{"name": "node", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "preserveGraph",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "node", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "graph remains connected",
                            "input": {"node": [[2], [1]]},
                            "expected": [[2], [1]],
                            "expectedMutations": {"node": [[2], [1]]},
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def preserveGraph(self, node: Optional[Node]) -> Optional[Node]:\n"
                "        clones = {}\n"
                "        def clone(current: Node) -> Node:\n"
                "            if current in clones:\n"
                "                return clones[current]\n"
                "            copied = Node(current.val)\n"
                "            clones[current] = copied\n"
                "            copied.neighbors = [clone(neighbor) for neighbor in current.neighbors]\n"
                "            return copied\n"
                "        return clone(node) if node is not None else None\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_quad_tree_node_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "quad-tree"},
                "java": {
                    "className": "Solution",
                    "methodName": "construct",
                    "returnType": "Node",
                    "parameters": [{"name": "grid", "type": "int[][]"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "construct",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "grid", "type": "List[List[int]]"}],
                },
            }
            expected = {
                "val": True,
                "isLeaf": False,
                "topLeft": {"val": True, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
                "topRight": {"val": False, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
                "bottomLeft": {"val": False, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
                "bottomRight": {"val": True, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "mixed quadrants",
                            "input": {"grid": [[1, 0], [0, 1]]},
                            "expected": expected,
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def construct(self, grid: List[List[int]]) -> Optional[Node]:\n"
                "        return Node(\n"
                "            False,\n"
                "            False,\n"
                "            Node(True, True),\n"
                "            Node(False, True),\n"
                "            Node(False, True),\n"
                "            Node(True, True),\n"
                "        )\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_rejects_malformed_quad_tree_outputs(self) -> None:
        invalid_solutions = [
            (
                "leaf with child",
                "class Solution:\n"
                "    def construct(self, grid: List[List[int]]) -> Optional[Node]:\n"
                "        return Node(True, True, Node(False, True), None, None, None)\n",
                "quad-tree leaf must not have children",
            ),
            (
                "internal with missing child",
                "class Solution:\n"
                "    def construct(self, grid: List[List[int]]) -> Optional[Node]:\n"
                "        return Node(True, False, Node(True, True), None, Node(False, True), Node(True, True))\n",
                "quad-tree internal node must have four children",
            ),
            (
                "cycle",
                "class Solution:\n"
                "    def construct(self, grid: List[List[int]]) -> Optional[Node]:\n"
                "        root = Node(True, False)\n"
                "        leaf = Node(True, True)\n"
                "        root.topLeft = root\n"
                "        root.topRight = leaf\n"
                "        root.bottomLeft = leaf\n"
                "        root.bottomRight = leaf\n"
                "        return root\n",
                "quad-tree Node output contains a cycle",
            ),
        ]
        for name, solution_source, expected_error in invalid_solutions:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                problem = valid_problem(root)
                problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
                problem_payload["signature"] = {
                    "customTypes": {"Node": "quad-tree"},
                    "java": {
                        "className": "Solution",
                        "methodName": "construct",
                        "returnType": "Node",
                        "parameters": [{"name": "grid", "type": "int[][]"}],
                    },
                    "python": {
                        "className": "Solution",
                        "methodName": "construct",
                        "returnType": "Optional[Node]",
                        "parameters": [{"name": "grid", "type": "List[List[int]]"}],
                    },
                }
                write_json(problem / "problem.json", problem_payload)
                write_json(
                    problem / "cases.json",
                    {
                        "source": "repo-authored-clean-room",
                        "matcher": {"type": "exact"},
                        "cases": [
                            {
                                "name": name,
                                "input": {"grid": [[1, 0], [0, 1]]},
                                "expected": quad_tree_node(
                                    quad_tree_leaf(True),
                                    quad_tree_leaf(False),
                                    quad_tree_leaf(False),
                                    quad_tree_leaf(True),
                                ),
                            }
                        ],
                    },
                )
                write_text(problem / "python" / "solution-1-brute-force" / "solution.py", solution_source)

                findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

                self.assertIn(expected_error, finding_messages(findings))

    def test_python_driver_snapshots_tree_node_expected_reference_before_solution_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "TreeNode",
                "parameters": [
                    {"name": "root", "type": "TreeNode"},
                    {"name": "p", "type": "TreeNode"},
                    {"name": "q", "type": "TreeNode"},
                ],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "Optional[TreeNode]",
                "parameters": [
                    {"name": "root", "type": "Optional[TreeNode]"},
                    {"name": "p", "type": "Optional[TreeNode]"},
                    {"name": "q", "type": "Optional[TreeNode]"},
                ],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "mutated expected path",
                            "input": {
                                "root": [9, 4, 13, 2, 6, 11, 15, None, 3, 5, 7],
                                "p": {"from": "root", "path": "LLR"},
                                "q": {"from": "root", "path": "LRL"},
                            },
                            "expected": {"from": "root", "path": "L"},
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def lowestCommonAncestor(self, root: Optional[TreeNode], p: Optional[TreeNode], q: Optional[TreeNode]) -> Optional[TreeNode]:\n"
                "        wrong = root.right\n"
                "        root.left = wrong\n"
                "        return wrong\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("expected {'from': 'root', 'path': 'L'} got [13, 11, 15]", finding_messages(findings))

    def test_python_driver_supports_balanced_bst_matcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "sortedArrayToBST",
                "returnType": "TreeNode",
                "parameters": [{"name": "nums", "type": "int[]"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "sortedArrayToBST",
                "returnType": "Optional[TreeNode]",
                "parameters": [{"name": "nums", "type": "List[int]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "balanced-bst-from-sorted-array"},
                    "cases": [
                        {
                            "name": "even length can choose upper middle",
                            "input": {"nums": [2, 5, 9, 12]},
                            "expected": [],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def sortedArrayToBST(self, nums: List[int]) -> Optional[TreeNode]:\n"
                "        def build(left: int, right: int) -> Optional[TreeNode]:\n"
                "            if left > right:\n"
                "                return None\n"
                "            mid = (left + right + 1) // 2\n"
                "            node = TreeNode(nums[mid])\n"
                "            node.left = build(left, mid - 1)\n"
                "            node.right = build(mid + 1, right)\n"
                "            return node\n"
                "        return build(0, len(nums) - 1)\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def sortedArrayToBST(self, nums: List[int]) -> Optional[TreeNode]:\n"
                "        dummy = TreeNode(0)\n"
                "        current = dummy\n"
                "        for value in nums:\n"
                "            current.right = TreeNode(value)\n"
                "            current = current.right\n"
                "        return dummy.right\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("case even length can choose upper middle expected [] got", finding_messages(findings))

    def test_python_driver_supports_unordered_nested_list_matcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "permute",
                "returnType": "List<List<Integer>>",
                "parameters": [{"name": "nums", "type": "int[]"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "permute",
                "returnType": "List[List[int]]",
                "parameters": [{"name": "nums", "type": "List[int]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "unordered-list-of-lists"},
                    "cases": [
                        {
                            "name": "same rows different order",
                            "input": {"nums": [2, 4, 6]},
                            "expected": [[2, 4, 6], [2, 6, 4], [4, 2, 6]],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def permute(self, nums: List[int]) -> List[List[int]]:\n"
                "        return [[4, 2, 6], [2, 6, 4], [2, 4, 6]]\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def permute(self, nums: List[int]) -> List[List[int]]:\n"
                "        return [[4, 2, 6], [2, 6, 4]]\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("case same rows different order expected", finding_messages(findings))

    def test_python_driver_supports_unordered_string_nested_list_matcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "groupAnagrams",
                "returnType": "List<List<String>>",
                "parameters": [{"name": "strs", "type": "String[]"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "groupAnagrams",
                "returnType": "List[List[str]]",
                "parameters": [{"name": "strs", "type": "List[str]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "unordered-list-of-lists"},
                    "cases": [
                        {
                            "name": "same groups different order",
                            "input": {"strs": ["arc", "car", "rat"]},
                            "expected": [["arc", "car"], ["rat"]],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:\n"
                "        return [[\"rat\"], [\"arc\", \"car\"]]\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_float_tolerance_matcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "average",
                "returnType": "List<Double>",
                "parameters": [{"name": "x", "type": "double"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "average",
                "returnType": "List[float]",
                "parameters": [{"name": "x", "type": "float"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "float-tolerance", "tolerance": 0.001},
                    "cases": [
                        {
                            "name": "close list",
                            "input": {"x": 2.0},
                            "expected": [1.5, 2.5],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def average(self, x: float) -> List[float]:\n"
                "        return [1.5005, 2.4995]\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def average(self, x: float) -> List[float]:\n"
                "        return [1.5, 2.7]\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("case close list expected", finding_messages(findings))

    def test_python_driver_supports_object_operations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "MinStack",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "push", "returnType": "void", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "pop", "returnType": "void", "parameters": []},
                        {"name": "top", "returnType": "int", "parameters": []},
                        {"name": "getMin", "returnType": "int", "parameters": []},
                    ],
                },
                "python": {
                    "className": "MinStack",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "push", "returnType": "None", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "pop", "returnType": "None", "parameters": []},
                        {"name": "top", "returnType": "int", "parameters": []},
                        {"name": "getMin", "returnType": "int", "parameters": []},
                    ],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "push pop and min",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "push", "input": {"val": 5}, "expected": None},
                                {"type": "call", "method": "push", "input": {"val": 2}, "expected": None},
                                {"type": "call", "method": "getMin", "input": {}, "expected": 2},
                                {"type": "call", "method": "pop", "input": {}, "expected": None},
                                {"type": "call", "method": "top", "input": {}, "expected": 5},
                            ],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class MinStack:\n"
                "    def __init__(self):\n"
                "        self.values = []\n"
                "        self.minimums = []\n"
                "    def push(self, val: int) -> None:\n"
                "        self.values.append(val)\n"
                "        if not self.minimums or val <= self.minimums[-1]:\n"
                "            self.minimums.append(val)\n"
                "    def pop(self) -> None:\n"
                "        val = self.values.pop()\n"
                "        if val == self.minimums[-1]:\n"
                "            self.minimums.pop()\n"
                "    def top(self) -> int:\n"
                "        return self.values[-1]\n"
                "    def getMin(self) -> int:\n"
                "        return self.minimums[-1]\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_object_driver_supports_scalar_char_returns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "StringIterator",
                    "constructor": {"parameters": [{"name": "compressedString", "type": "String"}]},
                    "methods": [{"name": "next", "returnType": "char", "parameters": []}],
                },
                "python": {
                    "className": "StringIterator",
                    "constructor": {"parameters": [{"name": "compressedString", "type": "str"}]},
                    "methods": [{"name": "next", "returnType": "str", "parameters": []}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "characters and exhausted sentinel",
                            "operations": [
                                {"type": "constructor", "input": {"compressedString": "a1"}, "expected": None},
                                {"type": "call", "method": "next", "input": {}, "expected": "a"},
                                {"type": "call", "method": "next", "input": {}, "expected": " "},
                            ],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class StringIterator:\n"
                "    def __init__(self, compressedString: str):\n"
                "        self.values = list(compressedString[0])\n"
                "        self.index = 0\n"
                "    def next(self) -> str:\n"
                "        if self.index >= len(self.values):\n"
                "            return ' '\n"
                "        value = self.values[self.index]\n"
                "        self.index += 1\n"
                "        return value\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_unordered_tree_list_matcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "generateTrees",
                "returnType": "List<TreeNode>",
                "parameters": [{"name": "n", "type": "int"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "generateTrees",
                "returnType": "List[Optional[TreeNode]]",
                "parameters": [{"name": "n", "type": "int"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "unordered-tree-list"},
                    "cases": [
                        {
                            "name": "two possible roots",
                            "input": {"n": 2},
                            "expected": [[1, None, 2], [2, 1]],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List, Optional\n\n"
                "class Solution:\n"
                "    def generateTrees(self, n: int) -> List[Optional[TreeNode]]:\n"
                "        right_root = TreeNode(2, TreeNode(1), None)\n"
                "        left_root = TreeNode(1, None, TreeNode(2))\n"
                "        return [right_root, left_root]\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_object_driver_uses_tolerance_only_for_floating_returns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "Stats",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "count", "returnType": "int", "parameters": []},
                        {"name": "average", "returnType": "double", "parameters": []},
                    ],
                },
                "python": {
                    "className": "Stats",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "count", "returnType": "int", "parameters": []},
                        {"name": "average", "returnType": "float", "parameters": []},
                    ],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "float-tolerance", "tolerance": 0.001},
                    "cases": [
                        {
                            "name": "mixed returns",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "count", "input": {}, "expected": 2},
                                {"type": "call", "method": "average", "input": {}, "expected": 2.5},
                            ],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Stats:\n"
                "    def count(self) -> int:\n"
                "        return 2\n"
                "    def average(self) -> float:\n"
                "        return 2.5005\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_object_driver_supports_one_of_int_returns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "RandomizedSet",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "insert", "returnType": "boolean", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "getRandom", "returnType": "int", "parameters": []},
                    ],
                },
                "python": {
                    "className": "RandomizedSet",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "insert", "returnType": "bool", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "getRandom", "returnType": "int", "parameters": []},
                    ],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "object-one-of"},
                    "cases": [
                        {
                            "name": "multi member set",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "insert", "input": {"val": 8}, "expected": True},
                                {"type": "call", "method": "insert", "input": {"val": 13}, "expected": True},
                                {"type": "call", "method": "getRandom", "input": {}, "expected": {"oneOf": [8, 13]}},
                            ],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class RandomizedSet:\n"
                "    def __init__(self) -> None:\n"
                "        self.values = []\n"
                "    def insert(self, val: int) -> bool:\n"
                "        self.values.append(val)\n"
                "        return True\n"
                "    def getRandom(self) -> int:\n"
                "        return self.values[-1]\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_generic_matcher_does_not_support_object_one_of(self) -> None:
        self.assertFalse(matches("object-one-of", 8, {"oneOf": [8, 13]}, {}, {}))

    def test_java_function_check_does_not_support_object_one_of(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported Java matcher/type: object-one-of/int"):
            java_check_expression("object-one-of", {}, "int", "actual", "expected", 1, {})

    def test_python_object_driver_rejects_one_of_miss(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "RandomizedSet",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "insert", "returnType": "boolean", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "getRandom", "returnType": "int", "parameters": []},
                    ],
                },
                "python": {
                    "className": "RandomizedSet",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "insert", "returnType": "bool", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "getRandom", "returnType": "int", "parameters": []},
                    ],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "object-one-of"},
                    "cases": [
                        {
                            "name": "reject non-member random value",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "insert", "input": {"val": 8}, "expected": True},
                                {"type": "call", "method": "insert", "input": {"val": 13}, "expected": True},
                                {"type": "call", "method": "getRandom", "input": {}, "expected": {"oneOf": [8, 13]}},
                            ],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class RandomizedSet:\n"
                "    def insert(self, val: int) -> bool:\n"
                "        return True\n"
                "    def getRandom(self) -> int:\n"
                "        return 99\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("expected {'oneOf': [8, 13]} got 99", finding_messages(findings))

    def test_python_driver_supports_unordered_flat_list_matcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "letterCombinations",
                "returnType": "List<String>",
                "parameters": [{"name": "digits", "type": "String"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "letterCombinations",
                "returnType": "List[str]",
                "parameters": [{"name": "digits", "type": "str"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "unordered-list"},
                    "cases": [
                        {
                            "name": "same strings different order",
                            "input": {"digits": "8"},
                            "expected": ["t", "u", "v"],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def letterCombinations(self, digits: str) -> List[str]:\n"
                "        return ['v', 't', 'u']\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    def test_python_driver_supports_valid_topological_order_matcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "findOrder",
                "returnType": "int[]",
                "parameters": [
                    {"name": "numCourses", "type": "int"},
                    {"name": "prerequisites", "type": "int[][]"},
                ],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "findOrder",
                "returnType": "List[int]",
                "parameters": [
                    {"name": "numCourses", "type": "int"},
                    {"name": "prerequisites", "type": "List[List[int]]"},
                ],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "valid-topological-order"},
                    "cases": [
                        {
                            "name": "ambiguous order",
                            "input": {"numCourses": 4, "prerequisites": [[1, 0], [2, 0], [3, 1], [3, 2]]},
                            "expected": [0, 1, 2, 3],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:\n"
                "        return [0, 2, 1, 3]\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:\n"
                "        return [0, 3, 1, 2]\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("case ambiguous order expected", finding_messages(findings))

    def test_python_driver_rejects_malformed_topological_fixture_as_empty_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "findOrder",
                "returnType": "int[]",
                "parameters": [
                    {"name": "numCourses", "type": "int"},
                    {"name": "prerequisites", "type": "int[][]"},
                ],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "findOrder",
                "returnType": "List[int]",
                "parameters": [
                    {"name": "numCourses", "type": "int"},
                    {"name": "prerequisites", "type": "List[List[int]]"},
                ],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "valid-topological-order"},
                    "cases": [
                        {
                            "name": "malformed edge is not a cycle",
                            "input": {"numCourses": 3, "prerequisites": [[1, 0, 2]]},
                            "expected": [],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:\n"
                "        return []\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("case malformed edge is not a cycle expected", finding_messages(findings))

    def test_python_driver_rejects_rebuilt_list_node_output_when_identity_contract_is_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "ListNode",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "Optional[ListNode]",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "reverse compact chain",
                            "input": {"head": [4, 1, 9]},
                            "expected": [9, 1, 4],
                            "linkedListContract": {
                                "result": {"from": "head", "nodeIndices": [2, 1, 0]}
                            },
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:\n"
                "        values = []\n"
                "        while head is not None:\n"
                "            values.append(head.val)\n"
                "            head = head.next\n"
                "        dummy = ListNode(0)\n"
                "        tail = dummy\n"
                "        for value in reversed(values):\n"
                "            tail.next = ListNode(value)\n"
                "            tail = tail.next\n"
                "        return dummy.next\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn(
                "result linked-list nodes do not match expected input node identities",
                finding_messages(findings),
            )

    def test_python_driver_rejects_unrestored_list_node_post_call_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "isPalindrome",
                "returnType": "boolean",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "isPalindrome",
                "returnType": "bool",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "mismatch near tail",
                            "input": {"head": [9, 1, 9, 2]},
                            "expected": False,
                            "linkedListContract": {"postCall": {"head": [0, 1, 2, 3]}},
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def isPalindrome(self, head: Optional[ListNode]) -> bool:\n"
                "        slow = head\n"
                "        fast = head\n"
                "        while fast is not None and fast.next is not None:\n"
                "            slow = slow.next\n"
                "            fast = fast.next.next\n"
                "        previous = None\n"
                "        while slow is not None:\n"
                "            following = slow.next\n"
                "            slow.next = previous\n"
                "            previous = slow\n"
                "            slow = following\n"
                "        return False\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn(
                "post-call linked-list nodes for head do not match expected input identities",
                finding_messages(findings),
            )

    def test_python_driver_reports_cyclic_list_node_return(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "cycle",
                "returnType": "ListNode",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "cycle",
                "returnType": "Optional[ListNode]",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "cycle output",
                            "input": {"head": [1, 2]},
                            "expected": [1, 2],
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "class Solution:\n"
                "    def cycle(self, head: Optional[ListNode]) -> Optional[ListNode]:\n"
                "        if head is not None:\n"
                "            head.next = head\n"
                "        return head\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("returned invalid ListNode: ListNode output contains a cycle", finding_messages(findings))

    def test_python_driver_reports_failed_mutation_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["python"]["returnType"] = "int"
            problem_payload["signature"]["python"]["methodName"] = "removeElement"
            problem_payload["signature"]["python"]["parameters"] = [
                {"name": "nums", "type": "List[int]"},
                {"name": "val", "type": "int"},
            ]
            problem_payload["signature"]["java"]["returnType"] = "int"
            problem_payload["signature"]["java"]["methodName"] = "removeElement"
            problem_payload["signature"]["java"]["parameters"] = [
                {"name": "nums", "type": "int[]"},
                {"name": "val", "type": "int"},
            ]
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                        "name": "remove matching value",
                        "input": {"nums": [3, 1, 3, 2], "val": 3},
                        "expected": 2,
                            "expectedMutations": {"nums": {"prefix": [1, 2], "lengthFrom": "return"}},
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def removeElement(self, nums: List[int], val: int) -> int:\n"
                "        return 2\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertIn("case remove matching value expected mutation nums", finding_messages(findings))

    def test_python_driver_supports_char_grid_mutation_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "solve",
                "returnType": "void",
                "parameters": [{"name": "board", "type": "char[][]"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "solve",
                "returnType": "None",
                "parameters": [{"name": "board", "type": "List[List[str]]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "capture center",
                            "input": {"board": [["X", "X", "X"], ["X", "O", "X"], ["X", "X", "X"]]},
                            "expected": None,
                            "expectedMutations": {"board": [["X", "X", "X"], ["X", "X", "X"], ["X", "X", "X"]]},
                        }
                    ],
                },
            )
            write_text(
                problem / "python" / "solution-1-brute-force" / "solution.py",
                "from typing import List\n\n"
                "class Solution:\n"
                "    def solve(self, board: List[List[str]]) -> None:\n"
                "        board[1][1] = 'X'\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "python", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_rejects_raw_nested_list_rows_for_unordered_matcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "permute",
                "returnType": "List<List<Integer>>",
                "parameters": [{"name": "nums", "type": "int[]"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "permute",
                "returnType": "List[List[int]]",
                "parameters": [{"name": "nums", "type": "List[int]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "unordered-list-of-lists"},
                    "cases": [
                        {
                            "name": "integer rows only",
                            "input": {"nums": [1, 2]},
                            "expected": [[1, 2], [2, 1]],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class Solution {\n"
                "    @SuppressWarnings({\"rawtypes\", \"unchecked\"})\n"
                "    public List<List<Integer>> permute(int[] nums) {\n"
                "        List raw = new ArrayList();\n"
                "        raw.add(Arrays.asList(\"1\", \"2\"));\n"
                "        raw.add(Arrays.asList(\"2\", \"1\"));\n"
                "        return raw;\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertIn("java driver failed for solution-1-brute-force", finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_unordered_int_matrix_matcher_preserves_duplicate_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "closest",
                "returnType": "int[][]",
                "parameters": [{"name": "points", "type": "int[][]"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "closest",
                "returnType": "List[List[int]]",
                "parameters": [{"name": "points", "type": "List[List[int]]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "unordered-list-of-lists"},
                    "cases": [
                        {
                            "name": "duplicate rows are counted",
                            "input": {"points": [[1, 1], [1, 1], [2, 2]]},
                            "expected": [[1, 1], [1, 1], [2, 2]],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class Solution {\n"
                "    public int[][] closest(int[][] points) {\n"
                "        return new int[][] {new int[] {2, 2}, new int[] {1, 1}, new int[] {1, 1}};\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))

            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class Solution {\n"
                "    public int[][] closest(int[][] points) {\n"
                "        return new int[][] {new int[] {2, 2}, new int[] {1, 1}};\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertIn("java driver failed for solution-1-brute-force", finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_supports_unordered_string_nested_list_matcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "groupAnagrams",
                "returnType": "List<List<String>>",
                "parameters": [{"name": "strs", "type": "String[]"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "groupAnagrams",
                "returnType": "List[List[str]]",
                "parameters": [{"name": "strs", "type": "List[str]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "unordered-list-of-lists"},
                    "cases": [
                        {
                            "name": "same groups different order",
                            "input": {"strs": ["arc", "car", "rat"]},
                            "expected": [["arc", "car"], ["rat"]],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class Solution {\n"
                "    public List<List<String>> groupAnagrams(String[] strs) {\n"
                "        return Arrays.asList(Arrays.asList(\"rat\"), Arrays.asList(\"arc\", \"car\"));\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_supports_list_double_float_tolerance_matcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "average",
                "returnType": "List<Double>",
                "parameters": [{"name": "x", "type": "double"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "average",
                "returnType": "List[float]",
                "parameters": [{"name": "x", "type": "float"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "float-tolerance", "tolerance": 0.001},
                    "cases": [
                        {
                            "name": "close list",
                            "input": {"x": 2.0},
                            "expected": [1.5, 2.5],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class Solution {\n"
                "    public List<Double> average(double x) {\n"
                "        return Arrays.asList(1.5005d, 2.4995d);\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_supports_double_array_and_nested_string_parameters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "calcEquation",
                "returnType": "double[]",
                "parameters": [
                    {"name": "equations", "type": "List<List<String>>"},
                    {"name": "values", "type": "double[]"},
                    {"name": "queries", "type": "List<List<String>>"},
                ],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "calcEquation",
                "returnType": "List[float]",
                "parameters": [
                    {"name": "equations", "type": "List[List[str]]"},
                    {"name": "values", "type": "List[float]"},
                    {"name": "queries", "type": "List[List[str]]"},
                ],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "float-tolerance", "tolerance": 0.001},
                    "cases": [
                        {
                            "name": "close ratios",
                            "input": {
                                "equations": [["a", "b"], ["b", "c"]],
                                "values": [2.0, 3.0],
                                "queries": [["a", "c"], ["b", "a"], ["x", "x"]],
                            },
                            "expected": [6.0, 0.5, -1.0],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class Solution {\n"
                "    public double[] calcEquation(List<List<String>> equations, double[] values, List<List<String>> queries) {\n"
                "        return new double[] {values[0] * values[1] + 0.0005d, 1.0d / values[0] - 0.0005d, -1.0d};\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_supports_object_operations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "MinStack",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "push", "returnType": "void", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "pop", "returnType": "void", "parameters": []},
                        {"name": "top", "returnType": "int", "parameters": []},
                        {"name": "getMin", "returnType": "int", "parameters": []},
                    ],
                },
                "python": {
                    "className": "MinStack",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "push", "returnType": "None", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "pop", "returnType": "None", "parameters": []},
                        {"name": "top", "returnType": "int", "parameters": []},
                        {"name": "getMin", "returnType": "int", "parameters": []},
                    ],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "push pop and min",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "push", "input": {"val": 5}, "expected": None},
                                {"type": "call", "method": "push", "input": {"val": 2}, "expected": None},
                                {"type": "call", "method": "getMin", "input": {}, "expected": 2},
                                {"type": "call", "method": "pop", "input": {}, "expected": None},
                                {"type": "call", "method": "top", "input": {}, "expected": 5},
                            ],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class MinStack {\n"
                "    private final Deque<Integer> values = new ArrayDeque<>();\n"
                "    private final Deque<Integer> minimums = new ArrayDeque<>();\n"
                "    public void push(int val) {\n"
                "        values.push(val);\n"
                "        if (minimums.isEmpty() || val <= minimums.peek()) minimums.push(val);\n"
                "    }\n"
                "    public void pop() {\n"
                "        int val = values.pop();\n"
                "        if (val == minimums.peek()) minimums.pop();\n"
                "    }\n"
                "    public int top() { return values.peek(); }\n"
                "    public int getMin() { return minimums.peek(); }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_object_driver_supports_scalar_char_returns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "StringIterator",
                    "constructor": {"parameters": [{"name": "compressedString", "type": "String"}]},
                    "methods": [{"name": "next", "returnType": "char", "parameters": []}],
                },
                "python": {
                    "className": "StringIterator",
                    "constructor": {"parameters": [{"name": "compressedString", "type": "str"}]},
                    "methods": [{"name": "next", "returnType": "str", "parameters": []}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "characters and exhausted sentinel",
                            "operations": [
                                {"type": "constructor", "input": {"compressedString": "a1"}, "expected": None},
                                {"type": "call", "method": "next", "input": {}, "expected": "a"},
                                {"type": "call", "method": "next", "input": {}, "expected": " "},
                            ],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class StringIterator {\n"
                "    private final char[] values;\n"
                "    private int index;\n"
                "    public StringIterator(String compressedString) {\n"
                "        values = new char[] {compressedString.charAt(0)};\n"
                "    }\n"
                "    public char next() {\n"
                "        if (index >= values.length) return ' ';\n"
                "        return values[index++];\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_supports_unordered_tree_list_matcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "generateTrees",
                "returnType": "List<TreeNode>",
                "parameters": [{"name": "n", "type": "int"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "generateTrees",
                "returnType": "List[Optional[TreeNode]]",
                "parameters": [{"name": "n", "type": "int"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "unordered-tree-list"},
                    "cases": [
                        {
                            "name": "two possible roots",
                            "input": {"n": 2},
                            "expected": [[1, None, 2], [2, 1]],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class Solution {\n"
                "    public List<TreeNode> generateTrees(int n) {\n"
                "        TreeNode rightRoot = new TreeNode(2, new TreeNode(1), null);\n"
                "        TreeNode leftRoot = new TreeNode(1, null, new TreeNode(2));\n"
                "        return Arrays.asList(rightRoot, leftRoot);\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_object_driver_uses_tolerance_only_for_floating_returns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "Stats",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "count", "returnType": "int", "parameters": []},
                        {"name": "average", "returnType": "double", "parameters": []},
                    ],
                },
                "python": {
                    "className": "Stats",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "count", "returnType": "int", "parameters": []},
                        {"name": "average", "returnType": "float", "parameters": []},
                    ],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "float-tolerance", "tolerance": 0.001},
                    "cases": [
                        {
                            "name": "mixed returns",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "count", "input": {}, "expected": 2},
                                {"type": "call", "method": "average", "input": {}, "expected": 2.5},
                            ],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class Stats {\n"
                "    public int count() { return 2; }\n"
                "    public double average() { return 2.5005d; }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_object_driver_supports_one_of_int_returns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "RandomizedSet",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "insert", "returnType": "boolean", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "getRandom", "returnType": "int", "parameters": []},
                    ],
                },
                "python": {
                    "className": "RandomizedSet",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "insert", "returnType": "bool", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "getRandom", "returnType": "int", "parameters": []},
                    ],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "object-one-of"},
                    "cases": [
                        {
                            "name": "multi member set",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "insert", "input": {"val": 8}, "expected": True},
                                {"type": "call", "method": "insert", "input": {"val": 13}, "expected": True},
                                {"type": "call", "method": "getRandom", "input": {}, "expected": {"oneOf": [8, 13]}},
                            ],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class RandomizedSet {\n"
                "    private final List<Integer> values = new ArrayList<>();\n"
                "    public boolean insert(int val) { values.add(val); return true; }\n"
                "    public int getRandom() { return values.get(values.size() - 1); }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_object_driver_rejects_one_of_miss(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "RandomizedSet",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "insert", "returnType": "boolean", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "getRandom", "returnType": "int", "parameters": []},
                    ],
                },
                "python": {
                    "className": "RandomizedSet",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "insert", "returnType": "bool", "parameters": [{"name": "val", "type": "int"}]},
                        {"name": "getRandom", "returnType": "int", "parameters": []},
                    ],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "object-one-of"},
                    "cases": [
                        {
                            "name": "reject non-member random value",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "insert", "input": {"val": 8}, "expected": True},
                                {"type": "call", "method": "insert", "input": {"val": 13}, "expected": True},
                                {"type": "call", "method": "getRandom", "input": {}, "expected": {"oneOf": [8, 13]}},
                            ],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class RandomizedSet {\n"
                "    public boolean insert(int val) { return true; }\n"
                "    public int getRandom() { return 99; }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertIn("java driver failed", finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_object_driver_supports_double_array_float_tolerance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "kind": "object",
                "java": {
                    "className": "WindowStats",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "values", "returnType": "double[]", "parameters": []}
                    ],
                },
                "python": {
                    "className": "WindowStats",
                    "constructor": {"parameters": []},
                    "methods": [
                        {"name": "values", "returnType": "List[float]", "parameters": []}
                    ],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "float-tolerance", "tolerance": 0.001},
                    "cases": [
                        {
                            "name": "array return",
                            "operations": [
                                {"type": "constructor", "input": {}, "expected": None},
                                {"type": "call", "method": "values", "input": {}, "expected": [1.5, 2.5]},
                            ],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class WindowStats {\n"
                "    public double[] values() { return new double[] {1.5005d, 2.4995d}; }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_runs_solution_tier_without_repo_class_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class Solution {\n"
                "    public int[] twoSum(int[] nums, int target) {\n"
                "        for (int i = 0; i < nums.length; i++) {\n"
                "            for (int j = i + 1; j < nums.length; j++) {\n"
                "                if (nums[i] + nums[j] == target) {\n"
                "                    return new int[] {i, j};\n"
                "                }\n"
                "            }\n"
                "        }\n"
                "        return new int[] {};\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_runs_list_node_solution_tier_without_repo_class_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "ListNode",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "Optional[ListNode]",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "reverse compact chain",
                            "input": {"head": [4, 1, 9]},
                            "expected": [9, 1, 4],
                            "linkedListContract": {
                                "result": {"from": "head", "nodeIndices": [2, 1, 0]}
                            },
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class Solution {\n"
                "    public ListNode reverseList(ListNode head) {\n"
                "        ListNode previous = null;\n"
                "        ListNode current = head;\n"
                "        while (current != null) {\n"
                "            ListNode next = current.next;\n"
                "            current.next = previous;\n"
                "            previous = current;\n"
                "            current = next;\n"
                "        }\n"
                "        return previous;\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_runs_tree_node_identity_reference_solution_tier_without_repo_class_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "TreeNode",
                "parameters": [
                    {"name": "root", "type": "TreeNode"},
                    {"name": "p", "type": "TreeNode"},
                    {"name": "q", "type": "TreeNode"},
                ],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "Optional[TreeNode]",
                "parameters": [
                    {"name": "root", "type": "Optional[TreeNode]"},
                    {"name": "p", "type": "Optional[TreeNode]"},
                    {"name": "q", "type": "Optional[TreeNode]"},
                ],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "identity lca",
                            "input": {
                                "root": [9, 4, 13, 2, 6, 11, 15, None, 3, 5, 7],
                                "p": {"from": "root", "path": "LLR"},
                                "q": {"from": "root", "path": "LRL"},
                            },
                            "expected": {"from": "root", "path": "L"},
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class Solution {\n"
                "    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {\n"
                "        if (root == null || root == p || root == q) {\n"
                "            return root;\n"
                "        }\n"
                "        TreeNode left = lowestCommonAncestor(root.left, p, q);\n"
                "        TreeNode right = lowestCommonAncestor(root.right, p, q);\n"
                "        if (left != null && right != null) {\n"
                "            return root;\n"
                "        }\n"
                "        return left != null ? left : right;\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_rejects_rebuilt_tree_node_when_identity_reference_expected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "TreeNode",
                "parameters": [
                    {"name": "root", "type": "TreeNode"},
                    {"name": "p", "type": "TreeNode"},
                    {"name": "q", "type": "TreeNode"},
                ],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "Optional[TreeNode]",
                "parameters": [
                    {"name": "root", "type": "Optional[TreeNode]"},
                    {"name": "p", "type": "Optional[TreeNode]"},
                    {"name": "q", "type": "Optional[TreeNode]"},
                ],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "rebuilt node fails identity",
                            "input": {
                                "root": [9, 4, 13, 2, 6, 11, 15, None, 3, 5, 7],
                                "p": {"from": "root", "path": "LLR"},
                                "q": {"from": "root", "path": "LRL"},
                            },
                            "expected": {"from": "root", "path": "L"},
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class Solution {\n"
                "    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {\n"
                "        return new TreeNode(4);\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertIn("java driver failed", finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_supports_tree_node_mutation_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "flatten",
                "returnType": "void",
                "parameters": [{"name": "root", "type": "TreeNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "flatten",
                "returnType": "None",
                "parameters": [{"name": "root", "type": "Optional[TreeNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "flatten mutation",
                            "input": {"root": [1, 2, 3]},
                            "expected": None,
                            "expectedMutations": {"root": [1, None, 2, None, 3]},
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class Solution {\n"
                "    public void flatten(TreeNode root) {\n"
                "        List<TreeNode> nodes = new ArrayList<>();\n"
                "        preorder(root, nodes);\n"
                "        for (int i = 0; i < nodes.size(); i++) {\n"
                "            TreeNode node = nodes.get(i);\n"
                "            node.left = null;\n"
                "            node.right = i + 1 < nodes.size() ? nodes.get(i + 1) : null;\n"
                "        }\n"
                "    }\n"
                "    private void preorder(TreeNode node, List<TreeNode> nodes) {\n"
                "        if (node == null) return;\n"
                "        nodes.add(node);\n"
                "        preorder(node.left, nodes);\n"
                "        preorder(node.right, nodes);\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_supports_binary_tree_next_node_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "binary-tree-next"},
                "java": {
                    "className": "Solution",
                    "methodName": "connect",
                    "returnType": "Node",
                    "parameters": [{"name": "root", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "connect",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "root", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "ragged next levels",
                            "input": {"root": [1, 2, 3, None, 4, None, 5]},
                            "expected": [[1], [2, 3], [4, 5]],
                            "expectedMutations": {"root": [[1], [2, 3], [4, 5]]},
                        },
                        {
                            "name": "empty tree",
                            "input": {"root": []},
                            "expected": [],
                            "expectedMutations": {"root": []},
                        },
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class Solution {\n"
                "    public Node connect(Node root) {\n"
                "        List<Node> level = new ArrayList<>();\n"
                "        if (root != null) {\n"
                "            level.add(root);\n"
                "        }\n"
                "        while (!level.isEmpty()) {\n"
                "            List<Node> nextLevel = new ArrayList<>();\n"
                "            Node previous = null;\n"
                "            for (Node node : level) {\n"
                "                if (previous != null) {\n"
                "                    previous.next = node;\n"
                "                }\n"
                "                previous = node;\n"
                "                if (node.left != null) {\n"
                "                    nextLevel.add(node.left);\n"
                "                }\n"
                "                if (node.right != null) {\n"
                "                    nextLevel.add(node.right);\n"
                "                }\n"
                "            }\n"
                "            if (previous != null) {\n"
                "                previous.next = null;\n"
                "            }\n"
                "            level = nextLevel;\n"
                "        }\n"
                "        return root;\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_supports_random_list_node_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "random-list"},
                "java": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Node",
                    "parameters": [{"name": "head", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "head", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "random pointers by index",
                            "input": {"head": [[8, None], [12, 0], [5, 2]]},
                            "expected": [[8, None], [12, 0], [5, 2]],
                        },
                        {
                            "name": "empty list",
                            "input": {"head": []},
                            "expected": [],
                        },
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class Solution {\n"
                "    public Node copyRandomList(Node head) {\n"
                "        if (head == null) {\n"
                "            return null;\n"
                "        }\n"
                "        Map<Node, Node> clones = new IdentityHashMap<>();\n"
                "        Node current = head;\n"
                "        while (current != null) {\n"
                "            clones.put(current, new Node(current.val));\n"
                "            current = current.next;\n"
                "        }\n"
                "        current = head;\n"
                "        while (current != null) {\n"
                "            Node clone = clones.get(current);\n"
                "            clone.next = clones.get(current.next);\n"
                "            clone.random = clones.get(current.random);\n"
                "            current = current.next;\n"
                "        }\n"
                "        return clones.get(head);\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_rejects_random_list_reusing_input_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "random-list"},
                "java": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Node",
                    "parameters": [{"name": "head", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "copyRandomList",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "head", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "identity reuse is invalid",
                            "input": {"head": [[4, None], [9, 0]]},
                            "expected": [[4, None], [9, 0]],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class Solution {\n"
                "    public Node copyRandomList(Node head) {\n"
                "        return head;\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertIn("java driver failed", finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_supports_graph_node_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "graph"},
                "java": {
                    "className": "Solution",
                    "methodName": "cloneGraph",
                    "returnType": "Node",
                    "parameters": [{"name": "node", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "cloneGraph",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "node", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "triangle",
                            "input": {"node": [[2, 3], [1, 3], [1, 2]]},
                            "expected": [[2, 3], [1, 3], [1, 2]],
                        },
                        {
                            "name": "empty graph",
                            "input": {"node": []},
                            "expected": [],
                        },
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class Solution {\n"
                "    public Node cloneGraph(Node node) {\n"
                "        if (node == null) {\n"
                "            return null;\n"
                "        }\n"
                "        Map<Node, Node> clones = new IdentityHashMap<>();\n"
                "        return clone(node, clones);\n"
                "    }\n"
                "    private Node clone(Node node, Map<Node, Node> clones) {\n"
                "        if (clones.containsKey(node)) {\n"
                "            return clones.get(node);\n"
                "        }\n"
                "        Node copied = new Node(node.val);\n"
                "        clones.put(node, copied);\n"
                "        for (Node neighbor : node.neighbors) {\n"
                "            copied.neighbors.add(clone(neighbor, clones));\n"
                "        }\n"
                "        return copied;\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_rejects_graph_reusing_input_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "graph"},
                "java": {
                    "className": "Solution",
                    "methodName": "cloneGraph",
                    "returnType": "Node",
                    "parameters": [{"name": "node", "type": "Node"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "cloneGraph",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "node", "type": "Optional[Node]"}],
                },
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "identity reuse is invalid",
                            "input": {"node": [[2], [1]]},
                            "expected": [[2], [1]],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class Solution {\n"
                "    public Node cloneGraph(Node node) {\n"
                "        return node;\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertIn("java driver failed", finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_supports_quad_tree_node_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"] = {
                "customTypes": {"Node": "quad-tree"},
                "java": {
                    "className": "Solution",
                    "methodName": "construct",
                    "returnType": "Node",
                    "parameters": [{"name": "grid", "type": "int[][]"}],
                },
                "python": {
                    "className": "Solution",
                    "methodName": "construct",
                    "returnType": "Optional[Node]",
                    "parameters": [{"name": "grid", "type": "List[List[int]]"}],
                },
            }
            expected = {
                "val": True,
                "isLeaf": False,
                "topLeft": {"val": True, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
                "topRight": {"val": False, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
                "bottomLeft": {"val": False, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
                "bottomRight": {"val": True, "isLeaf": True, "topLeft": None, "topRight": None, "bottomLeft": None, "bottomRight": None},
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "mixed quadrants",
                            "input": {"grid": [[1, 0], [0, 1]]},
                            "expected": expected,
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class Solution {\n"
                "    public Node construct(int[][] grid) {\n"
                "        return new Node(\n"
                "            false,\n"
                "            false,\n"
                "            new Node(true, true),\n"
                "            new Node(false, true),\n"
                "            new Node(false, true),\n"
                "            new Node(true, true)\n"
                "        );\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_rejects_malformed_quad_tree_outputs(self) -> None:
        invalid_solutions = [
            (
                "leaf with child",
                "class Solution {\n"
                "    public Node construct(int[][] grid) {\n"
                "        return new Node(true, true, new Node(false, true), null, null, null);\n"
                "    }\n"
                "}\n",
            ),
            (
                "internal with missing child",
                "class Solution {\n"
                "    public Node construct(int[][] grid) {\n"
                "        return new Node(true, false, new Node(true, true), null, new Node(false, true), new Node(true, true));\n"
                "    }\n"
                "}\n",
            ),
            (
                "cycle",
                "class Solution {\n"
                "    public Node construct(int[][] grid) {\n"
                "        Node root = new Node(true, false);\n"
                "        Node leaf = new Node(true, true);\n"
                "        root.topLeft = root;\n"
                "        root.topRight = leaf;\n"
                "        root.bottomLeft = leaf;\n"
                "        root.bottomRight = leaf;\n"
                "        return root;\n"
                "    }\n"
                "}\n",
            ),
        ]
        for name, solution_source in invalid_solutions:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                problem = valid_problem(root)
                problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
                problem_payload["signature"] = {
                    "customTypes": {"Node": "quad-tree"},
                    "java": {
                        "className": "Solution",
                        "methodName": "construct",
                        "returnType": "Node",
                        "parameters": [{"name": "grid", "type": "int[][]"}],
                    },
                    "python": {
                        "className": "Solution",
                        "methodName": "construct",
                        "returnType": "Optional[Node]",
                        "parameters": [{"name": "grid", "type": "List[List[int]]"}],
                    },
                }
                write_json(problem / "problem.json", problem_payload)
                write_json(
                    problem / "cases.json",
                    {
                        "source": "repo-authored-clean-room",
                        "matcher": {"type": "exact"},
                        "cases": [
                            {
                                "name": name,
                                "input": {"grid": [[1, 0], [0, 1]]},
                                "expected": quad_tree_node(
                                    quad_tree_leaf(True),
                                    quad_tree_leaf(False),
                                    quad_tree_leaf(False),
                                    quad_tree_leaf(True),
                                ),
                            }
                        ],
                    },
                )
                write_text(problem / "java" / "solution-1-brute-force" / "Solution.java", solution_source)

                findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

                self.assertIn("java driver failed", finding_messages(findings))
                self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_snapshots_tree_node_expected_reference_before_solution_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "TreeNode",
                "parameters": [
                    {"name": "root", "type": "TreeNode"},
                    {"name": "p", "type": "TreeNode"},
                    {"name": "q", "type": "TreeNode"},
                ],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "lowestCommonAncestor",
                "returnType": "Optional[TreeNode]",
                "parameters": [
                    {"name": "root", "type": "Optional[TreeNode]"},
                    {"name": "p", "type": "Optional[TreeNode]"},
                    {"name": "q", "type": "Optional[TreeNode]"},
                ],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "mutated expected path",
                            "input": {
                                "root": [9, 4, 13, 2, 6, 11, 15, None, 3, 5, 7],
                                "p": {"from": "root", "path": "LLR"},
                                "q": {"from": "root", "path": "LRL"},
                            },
                            "expected": {"from": "root", "path": "L"},
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class Solution {\n"
                "    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {\n"
                "        TreeNode wrong = root.right;\n"
                "        root.left = wrong;\n"
                "        return wrong;\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertIn("java driver failed", finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_runs_cyclic_list_node_solution_tier_without_repo_class_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "hasCycle",
                "returnType": "boolean",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "hasCycle",
                "returnType": "bool",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "cycle to middle",
                            "input": {"head": {"values": [6, 1, 8, 5], "cycleTo": 2}},
                            "expected": True,
                        },
                        {
                            "name": "acyclic chain",
                            "input": {"head": [1, 2, 3]},
                            "expected": False,
                        },
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class Solution {\n"
                "    public boolean hasCycle(ListNode head) {\n"
                "        Set<ListNode> seen = Collections.newSetFromMap(new IdentityHashMap<>());\n"
                "        ListNode current = head;\n"
                "        while (current != null) {\n"
                "            if (!seen.add(current)) {\n"
                "                return true;\n"
                "            }\n"
                "            current = current.next;\n"
                "        }\n"
                "        return false;\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_supports_list_node_array_parameters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "mergeKLists",
                "returnType": "ListNode",
                "parameters": [{"name": "lists", "type": "ListNode[]"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "mergeKLists",
                "returnType": "Optional[ListNode]",
                "parameters": [{"name": "lists", "type": "List[Optional[ListNode]]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "three chains",
                            "input": {"lists": [[1, 4], None, [2, 3]]},
                            "expected": [1, 2, 3, 4],
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.*;\n\n"
                "class Solution {\n"
                "    public ListNode mergeKLists(ListNode[] lists) {\n"
                "        List<Integer> values = new ArrayList<>();\n"
                "        for (ListNode head : lists) {\n"
                "            while (head != null) {\n"
                "                values.add(head.val);\n"
                "                head = head.next;\n"
                "            }\n"
                "        }\n"
                "        Collections.sort(values);\n"
                "        ListNode dummy = new ListNode(0);\n"
                "        ListNode tail = dummy;\n"
                "        for (int value : values) {\n"
                "            tail.next = new ListNode(value);\n"
                "            tail = tail.next;\n"
                "        }\n"
                "        return dummy.next;\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertEqual([], findings, finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_rejects_rebuilt_list_node_output_when_identity_contract_is_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "ListNode",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "reverseList",
                "returnType": "Optional[ListNode]",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "reverse compact chain",
                            "input": {"head": [4, 1, 9]},
                            "expected": [9, 1, 4],
                            "linkedListContract": {
                                "result": {"from": "head", "nodeIndices": [2, 1, 0]}
                            },
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "import java.util.ArrayList;\n"
                "import java.util.List;\n\n"
                "class Solution {\n"
                "    public ListNode reverseList(ListNode head) {\n"
                "        List<Integer> values = new ArrayList<>();\n"
                "        while (head != null) {\n"
                "            values.add(head.val);\n"
                "            head = head.next;\n"
                "        }\n"
                "        ListNode dummy = new ListNode(0);\n"
                "        ListNode tail = dummy;\n"
                "        for (int i = values.size() - 1; i >= 0; i--) {\n"
                "            tail.next = new ListNode(values.get(i));\n"
                "            tail = tail.next;\n"
                "        }\n"
                "        return dummy.next;\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertIn("java driver failed for solution-1-brute-force", finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))

    @unittest.skipUnless(java_toolchain_available(), "Java toolchain not available")
    def test_java_driver_rejects_unrestored_list_node_post_call_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            problem = valid_problem(root)
            problem_payload = json.loads((problem / "problem.json").read_text(encoding="utf-8"))
            problem_payload["signature"]["java"] = {
                "className": "Solution",
                "methodName": "isPalindrome",
                "returnType": "boolean",
                "parameters": [{"name": "head", "type": "ListNode"}],
            }
            problem_payload["signature"]["python"] = {
                "className": "Solution",
                "methodName": "isPalindrome",
                "returnType": "bool",
                "parameters": [{"name": "head", "type": "Optional[ListNode]"}],
            }
            write_json(problem / "problem.json", problem_payload)
            write_json(
                problem / "cases.json",
                {
                    "source": "repo-authored-clean-room",
                    "matcher": {"type": "exact"},
                    "cases": [
                        {
                            "name": "mismatch near tail",
                            "input": {"head": [9, 1, 9, 2]},
                            "expected": False,
                            "linkedListContract": {"postCall": {"head": [0, 1, 2, 3]}},
                        }
                    ],
                },
            )
            write_text(
                problem / "java" / "solution-1-brute-force" / "Solution.java",
                "class Solution {\n"
                "    public boolean isPalindrome(ListNode head) {\n"
                "        ListNode slow = head;\n"
                "        ListNode fast = head;\n"
                "        while (fast != null && fast.next != null) {\n"
                "            slow = slow.next;\n"
                "            fast = fast.next.next;\n"
                "        }\n"
                "        ListNode previous = null;\n"
                "        while (slow != null) {\n"
                "            ListNode next = slow.next;\n"
                "            slow.next = previous;\n"
                "            previous = slow;\n"
                "            slow = next;\n"
                "        }\n"
                "        return false;\n"
                "    }\n"
                "}\n",
            )

            findings = run_problem_drivers(root, "lc-0001-two-sum", "java", allow_unsafe_driver_execution=True)

            self.assertIn("java driver failed for solution-1-brute-force", finding_messages(findings))
            self.assertEqual([], list(root.rglob("*.class")))


class CollectionRenderingTest(unittest.TestCase):
    def test_collection_pages_dedupe_shared_canonical_problem(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid_problem(root)
            for collection_id in ("leetcode-top-150", "grind-169"):
                manifest = valid_source_manifest(collection_id)
                manifest["items"][0]["group"] = "array"
                if collection_id == "grind-169":
                    manifest["items"][0]["title"] = "TWO SUM DRIFT"
                manifest["provenance"]["metadataSha256"] = source_metadata_hash(manifest["items"])
                write_json(
                    root / "resources" / "source-intake" / "coding-lists" / f"{collection_id}.json",
                    manifest,
                )

            pages = {page.path.name: page.content for page in render_collection_pages(root)}

            self.assertIn("| Unique canonical problems | 1 |", pages["README.md"])
            self.assertIn("| Problems appearing in multiple collections | 1 |", pages["README.md"])
            self.assertIn("[lc-0001-two-sum](../problem-bank/lc-0001-two-sum/)", pages["grind-169.md"])
            self.assertIn("| 1 | array | [lc-0001-two-sum]", pages["grind-169.md"])
            self.assertIn("| Two Sum |", pages["grind-169.md"])
            self.assertNotIn("TWO SUM DRIFT", pages["grind-169.md"])
            self.assertIn("| # | Group | Canonical problem | Title | Difficulty | Access |", pages["grind-169.md"])

class ScaffoldCommandTest(unittest.TestCase):
    def test_scaffold_creates_stub_from_source_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "grind-169.json",
                {
                    "collectionId": "grind-169",
                    "sourceStatus": "pinned",
                    "sourceUrl": "https://www.techinterviewhandbook.org/grind75/",
                    "expectedCount": 1,
                    "items": [
                        {
                            "sourceId": "704",
                            "title": "Binary Search",
                            "titleSlug": "binary-search",
                            "sourceUrl": "https://leetcode.com/problems/binary-search",
                            "collectionId": "grind-169",
                            "group": "binary-search",
                            "order": 1,
                            "difficulty": "easy",
                            "paidOnly": False,
                            "dedupeKey": "leetcode:704:binary-search",
                            "canonicalId": "lc-0704-binary-search",
                        }
                    ],
                },
            )

            result = run_python_command(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "scaffold_coding_problem.py"),
                    "lc-0704-binary-search",
                    "--root",
                    str(root),
                ],
                REPO_ROOT,
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            problem_dir = root / "05-coding-problems" / "problem-bank" / "lc-0704-binary-search"
            problem = json.loads((problem_dir / "problem.json").read_text(encoding="utf-8"))
            self.assertEqual("stub", problem["status"])
            self.assertEqual("704", problem["leetcode"]["frontendId"])
            self.assertFalse(problem["leetcode"]["paidOnly"])
            self.assertFalse((problem_dir / "solutions.json").exists())
            self.assertIn("Clean-Room Problem Summary", (problem_dir / "README.md").read_text(encoding="utf-8"))

    def test_scaffold_omits_paid_only_when_source_metadata_is_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "neetcode-all.json",
                {
                    "collectionId": "neetcode-all",
                    "sourceStatus": "pinned",
                    "sourceUrl": "https://neetcode.io/practice",
                    "expectedCount": 1,
                    "items": [
                        {
                            "sourceId": "704",
                            "title": "Binary Search",
                            "titleSlug": "binary-search",
                            "sourceUrl": "https://leetcode.com/problems/binary-search",
                            "collectionId": "neetcode-all",
                            "group": "Binary Search",
                            "order": 1,
                            "difficulty": "easy",
                            "dedupeKey": "leetcode:704:binary-search",
                            "canonicalId": "lc-0704-binary-search",
                        }
                    ],
                },
            )

            result = run_python_command(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "scaffold_coding_problem.py"),
                    "lc-0704-binary-search",
                    "--root",
                    str(root),
                ],
                REPO_ROOT,
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            problem = json.loads(
                (root / "05-coding-problems" / "problem-bank" / "lc-0704-binary-search" / "problem.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertNotIn("paidOnly", problem["leetcode"])

    def test_scaffold_preserves_paid_only_true_from_source_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "resources" / "source-intake" / "coding-lists" / "leetcode-top-150.json",
                {
                    "collectionId": "leetcode-top-150",
                    "sourceStatus": "pinned",
                    "sourceUrl": "https://leetcode.com/studyplan/top-interview-150/",
                    "expectedCount": 1,
                    "items": [
                        {
                            "sourceId": "9999",
                            "title": "Paid Example",
                            "titleSlug": "paid-example",
                            "sourceUrl": "https://leetcode.com/problems/paid-example",
                            "collectionId": "leetcode-top-150",
                            "group": "Array",
                            "order": 1,
                            "difficulty": "hard",
                            "paidOnly": True,
                            "dedupeKey": "leetcode:9999:paid-example",
                            "canonicalId": "lc-9999-paid-example",
                        }
                    ],
                },
            )

            result = run_python_command(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "scaffold_coding_problem.py"),
                    "lc-9999-paid-example",
                    "--root",
                    str(root),
                ],
                REPO_ROOT,
            )

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            problem = json.loads(
                (root / "05-coding-problems" / "problem-bank" / "lc-9999-paid-example" / "problem.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(problem["leetcode"]["paidOnly"])

    def test_scaffold_rejects_unsafe_canonical_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_python_command(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "scaffold_coding_problem.py"),
                    "../escape",
                    "--root",
                    tmp,
                ],
                REPO_ROOT,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("canonical_id must match", result.stderr)


if __name__ == "__main__":
    unittest.main()
