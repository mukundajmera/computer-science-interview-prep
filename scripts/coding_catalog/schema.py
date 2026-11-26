"""Schema checks for the coding problem catalog."""

from __future__ import annotations

import ast
import json
import keyword
import math
import os
import re
from datetime import date
from hashlib import sha256
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

COMPLETED_STATUSES = {"solution-draft", "verified", "reviewed"}
VALID_PROBLEM_STATUSES = {"metadata-only", "planned", "stub", *COMPLETED_STATUSES}
VALID_SOURCE_STATUSES = {"pinned", "blocked-source-unpinned"}
COLLECTION_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CANONICAL_ID_PATTERN = re.compile(r"^lc-[0-9]{4,}-[a-z0-9][a-z0-9-]*$")
SOURCE_URL_HOSTS = {"leetcode.com", "www.techinterviewhandbook.org", "neetcode.io"}
PROBLEM_URL_HOSTS = {"leetcode.com"}
REPO_AUTHORED = "repo-authored-clean-room"
SUPPORTED_MATCHERS = {
    "exact",
    "two-sum-indices",
    "balanced-bst-from-sorted-array",
    "unordered-list",
    "unordered-list-of-lists",
    "unordered-tree-list",
    "float-tolerance",
    "object-one-of",
    "valid-topological-order",
}
SOURCE_DIFFICULTIES = {"easy", "medium", "hard"}
SAFE_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
TITLE_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLAIN_METADATA_TEXT_PATTERN = re.compile(r"^[^\r\n`<>\[\]]+$")
PYTHON_BUILTIN_GENERIC_PATTERN = re.compile(r"\b(?:list|dict|tuple|set)\[")
JAVA_RESERVED_WORDS = {
    "abstract",
    "assert",
    "boolean",
    "break",
    "byte",
    "case",
    "catch",
    "char",
    "class",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extends",
    "final",
    "finally",
    "float",
    "for",
    "goto",
    "if",
    "implements",
    "import",
    "instanceof",
    "int",
    "interface",
    "long",
    "native",
    "new",
    "package",
    "private",
    "protected",
    "public",
    "return",
    "short",
    "static",
    "strictfp",
    "super",
    "switch",
    "synchronized",
    "this",
    "throw",
    "throws",
    "transient",
    "try",
    "void",
    "volatile",
    "while",
}
SUPPORTED_JAVA_PARAMETER_TYPES = {
    "int",
    "int[]",
    "int[][]",
    "int[][][]",
    "char[]",
    "char[][]",
    "double[]",
    "double",
    "float",
    "char",
    "boolean",
    "String",
    "String[]",
    "List<Integer>",
    "List<Double>",
    "List<String>",
    "List<List<Integer>>",
    "List<List<String>>",
    "ListNode",
    "ListNode[]",
    "Node",
    "TreeNode",
}
SUPPORTED_PYTHON_PARAMETER_TYPES = {
    "int",
    "float",
    "bool",
    "str",
    "List[int]",
    "List[float]",
    "List[List[int]]",
    "List[List[List[int]]]",
    "List[List[str]]",
    "List[str]",
    "List[Optional[ListNode]]",
    "Optional[Node]",
    "Optional[ListNode]",
    "Optional[TreeNode]",
}
SUPPORTED_JAVA_LIST_RETURN_TYPES = {
    "List<Double>",
    "List<Integer>",
    "List<String>",
    "List<TreeNode>",
    "List<List<Integer>>",
    "List<List<String>>",
}
JAVA_PARAMETER_ONLY_TYPES = {"ListNode[]"}
PYTHON_PARAMETER_ONLY_TYPES = {"List[Optional[ListNode]]"}
SUPPORTED_JAVA_RETURN_TYPES = {
    *(SUPPORTED_JAVA_PARAMETER_TYPES - JAVA_PARAMETER_ONLY_TYPES),
    *SUPPORTED_JAVA_LIST_RETURN_TYPES,
    "void",
}
SUPPORTED_PYTHON_RETURN_TYPES = {
    *(SUPPORTED_PYTHON_PARAMETER_TYPES - PYTHON_PARAMETER_ONLY_TYPES),
    "List[Optional[TreeNode]]",
    "None",
}
SUPPORTED_JAVA_MUTATION_TYPES = {"int[]", "int[][]", "char[]", "char[][]", "String[]", "ListNode", "Node", "TreeNode"}
SUPPORTED_PYTHON_MUTATION_TYPES = {
    "List[int]",
    "List[List[int]]",
    "List[List[str]]",
    "List[str]",
    "Optional[ListNode]",
    "Optional[Node]",
    "Optional[TreeNode]",
}
SUPPORTED_CUSTOM_NODE_TYPES = {"binary-tree-next", "graph", "quad-tree", "random-list"}
JAVA_TO_PYTHON_TYPES = {
    "int": "int",
    "double": "float",
    "float": "float",
    "char": "str",
    "int[]": "List[int]",
    "int[][]": "List[List[int]]",
    "int[][][]": "List[List[List[int]]]",
    "char[]": "List[str]",
    "char[][]": "List[List[str]]",
    "double[]": "List[float]",
    "boolean": "bool",
    "String": "str",
    "String[]": "List[str]",
    "List<Double>": "List[float]",
    "List<Integer>": "List[int]",
    "List<String>": "List[str]",
    "List<TreeNode>": "List[Optional[TreeNode]]",
    "List<List<Integer>>": "List[List[int]]",
    "List<List<String>>": "List[List[str]]",
    "ListNode": "Optional[ListNode]",
    "ListNode[]": "List[Optional[ListNode]]",
    "Node": "Optional[Node]",
    "TreeNode": "Optional[TreeNode]",
    "void": "None",
}
ALLOWED_CASE_KEYS = {"name", "input", "expected", "expectedMutations", "linkedListContract"}
ALLOWED_OBJECT_CASE_KEYS = {"name", "operations"}
ALLOWED_OBJECT_OPERATION_KEYS = {"type", "method", "input", "expected"}
ALLOWED_LINKED_LIST_CONTRACT_KEYS = {"result", "postCall"}
ALLOWED_LINKED_LIST_RESULT_KEYS = {"from", "nodeIndices"}
ALLOWED_PROBLEM_TOP_LEVEL_KEYS = {
    "cleanRoomReview",
    "collections",
    "difficulty",
    "id",
    "leetcode",
    "patterns",
    "provenance",
    "signature",
    "status",
    "title",
    "validation",
}
ALLOWED_LEETCODE_KEYS = {"frontendId", "paidOnly", "titleSlug", "url"}
ALLOWED_VALIDATION_KEYS = {"validatedAt", "checks"}
ALLOWED_VALIDATION_CHECK_KEYS = {"command", "language", "name", "reason", "status"}
VALIDATION_CHECK_CONTRACTS = {
    "catalog-strict": {
        "statuses": {"passed"},
        "language": None,
        "command": "python3 -B scripts/check_coding_problem_catalog.py --strict",
    },
    "driver-generation": {
        "statuses": {"passed"},
        "language": "java",
        "command": "python3 -B scripts/check_coding_problem_catalog.py --driver-generation",
    },
    "python-drivers": {
        "statuses": {"passed"},
        "language": "python",
        "command": "python3 -B scripts/check_coding_problem_catalog.py --drivers --allow-unsafe-driver-execution --language python",
    },
    "java-drivers": {
        "statuses": {"passed", "blocked"},
        "language": "java",
        "command": "python3 -B scripts/check_repo_smoke.py --only check_coding_problem_java_drivers --allow-unsafe-driver-execution",
        "blockedReason": "missing-jdk-11",
    },
}
VALIDATION_CHECK_STATUSES = {"passed", "blocked"}
VALIDATION_CHECK_LANGUAGES = {"java", "python"}
BLOCKED_SOURCE_HASHES_ENV = "CODING_BLOCKED_SOURCE_EXAMPLE_HASHES"
BLOCKED_SOURCE_HASH_FILE_ENV = "CODING_BLOCKED_SOURCE_EXAMPLE_HASH_FILE"
SHA256_HEX_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_SOURCE_TOP_LEVEL_KEYS = {
    "collectionId",
    "expectedCount",
    "items",
    "provenance",
    "snapshotDate",
    "sourceStatus",
    "sourceUrl",
}
SOURCE_ROUTE_ALLOWLIST = {
    "leetcode-top-150": "https://leetcode.com/studyplan/top-interview-150/",
    "grind-169": "https://www.techinterviewhandbook.org/grind75/",
    "neetcode-all": "https://neetcode.io/practice",
}
REQUIRED_SOURCE_PROVENANCE_KEYS = {
    "fetchDate",
    "sourcePages",
    "fetchMethod",
    "extractorVersion",
    "metadataSha256",
    "reviewReceipt",
    "rawSourceRetention",
}
REQUIRED_CLEAN_ROOM_SCOPE = {"problem.json", "README.md", "cases.json", "solutions.json"}
REQUIRED_CLEAN_ROOM_VERDICT = "no-source-statement-or-example-copying-detected"
ALLOWED_SOURCE_ITEM_KEYS = {
    "canonicalId",
    "collectionId",
    "dedupeKey",
    "difficulty",
    "group",
    "order",
    "paidOnly",
    "sourceId",
    "sourceUrl",
    "title",
    "titleSlug",
}
REQUIRED_SOURCE_ITEM_KEYS = {
    "canonicalId",
    "collectionId",
    "dedupeKey",
    "difficulty",
    "group",
    "order",
    "sourceId",
    "sourceUrl",
    "title",
    "titleSlug",
}
BLOCKED_SOURCE_TEXT_KEYS = {
    "answer",
    "constraints",
    "content",
    "description",
    "editorial",
    "example",
    "examples",
    "explanation",
    "hint",
    "hints",
    "prompt",
    "solution",
    "statement",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    path: str
    message: str


def error(path: Path | str, message: str) -> Finding:
    return Finding("error", str(path), message)


def warning(path: Path | str, message: str) -> Finding:
    return Finding("warning", str(path), message)


def require_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_catalog(
    catalog: list[dict[str, Any]],
    root: Path,
    require_source_manifests: bool = False,
) -> list[Finding]:
    findings: list[Finding] = []
    validate_blocked_source_hash_file_config(findings)
    seen_ids: dict[str, Path] = {}
    source_index = load_source_index(root)
    if require_source_manifests and not source_index:
        findings.append(error(root / "resources/source-intake/coding-lists", "strict mode requires source manifests"))

    for record in catalog:
        problem_dir = Path(record["dir"])
        problem_path = problem_dir / "problem.json"
        solutions_path = problem_dir / "solutions.json"
        cases_path = problem_dir / "cases.json"

        for parse_error in record.get("errors", []):
            if isinstance(parse_error, dict):
                findings.append(error(parse_error.get("path", problem_dir), str(parse_error.get("message", "invalid JSON"))))

        problem = record.get("problem")
        if not isinstance(problem, dict):
            findings.append(error(problem_path, "missing or invalid problem.json"))
            continue

        validate_allowed_keys(problem_path, problem, ALLOWED_PROBLEM_TOP_LEVEL_KEYS, "problem.json", findings)
        leetcode = problem.get("leetcode")
        if isinstance(leetcode, dict):
            validate_allowed_keys(problem_path, leetcode, ALLOWED_LEETCODE_KEYS, "problem.json.leetcode", findings)
            validate_problem_leetcode_metadata(problem_path, problem, source_index, findings)

        problem_id = problem.get("id")
        if not require_text(problem_id):
            findings.append(error(problem_path, "problem id is required"))
            continue
        if not CANONICAL_ID_PATTERN.fullmatch(problem_id):
            findings.append(error(problem_path, "problem id must match lc-<zero-padded-id>-<title-slug>"))

        if problem_id in seen_ids:
            findings.append(
                error(
                    problem_path,
                    f"duplicate canonical problem id {problem_id}; first seen at {seen_ids[problem_id]}",
                )
            )
        else:
            seen_ids[problem_id] = problem_path

        if problem_dir.name != problem_id:
            findings.append(error(problem_path, "problem id must match folder name"))

        collections = problem.get("collections", [])
        if not isinstance(collections, list):
            findings.append(error(problem_path, "collections must be a list"))
            collections = []
        collection_ids: set[str] = set()
        for collection in collections:
            collection_id = collection.get("id") if isinstance(collection, dict) else None
            if not require_text(collection_id):
                findings.append(error(problem_path, "collection id is required"))
                continue
            if not COLLECTION_ID_PATTERN.fullmatch(collection_id):
                findings.append(error(problem_path, f"collection id {collection_id} is not a safe slug"))
            if collection_id in collection_ids:
                findings.append(error(problem_path, f"duplicate collection membership {collection_id}"))
            collection_ids.add(collection_id)
            if isinstance(collection, dict):
                validate_url(
                    problem_path,
                    collection.get("sourceUrl"),
                    PROBLEM_URL_HOSTS,
                    f"collection {collection_id} sourceUrl",
                    findings,
                )
                validate_problem_collection_membership(problem_path, problem_id, collection, source_index, findings)
        validate_problem_collection_membership_set(problem_path, problem_id, collections, source_index, findings)

        status = problem.get("status")
        if status not in VALID_PROBLEM_STATUSES:
            findings.append(error(problem_path, f"status must be one of {sorted(VALID_PROBLEM_STATUSES)}"))
        completed = status in COMPLETED_STATUSES
        if completed:
            validate_signature(problem_path, problem, findings)
            validate_clean_room_provenance(problem_path, problem, findings)
            validate_clean_room_review(problem_dir, problem, findings)
            validate_validation_receipt(problem_path, problem, findings)

        cases_payload = record.get("cases")
        if completed:
            if not isinstance(cases_payload, dict):
                findings.append(error(cases_path, "completed problem must have cases.json"))
            else:
                validate_cases(cases_path, cases_payload, problem, findings)

        solutions_payload = record.get("solutions")
        if completed and not isinstance(solutions_payload, dict):
            findings.append(error(solutions_path, "completed problem must have solutions.json"))
            continue
        if not isinstance(solutions_payload, dict):
            continue

        if completed:
            validate_no_source_derived_keys(solutions_path, solutions_payload, "solutions.json", findings)

        solutions = solutions_payload.get("solutions", [])
        if not isinstance(solutions, list):
            findings.append(error(solutions_path, "solutions must be a list"))
            continue

        if completed:
            if not solutions:
                findings.append(error(solutions_path, "completed problem must have at least one solution"))
            if len(solutions) > 5:
                findings.append(error(solutions_path, "completed problem must not have more than five solutions"))

        validate_solution_tiers(problem_dir, solutions_path, solutions, findings, completed)

    return findings


def validate_signature(path: Path, problem: dict[str, Any], findings: list[Finding]) -> None:
    signature = problem.get("signature")
    if not isinstance(signature, dict):
        findings.append(error(path, "completed problem must define signature"))
        return
    kind = signature.get("kind", "function")
    validate_custom_types(path, signature, findings)
    if kind == "object":
        if function_signature_uses_node(signature):
            findings.append(error(path, "object signatures with custom Node are not supported by generated drivers"))
        validate_object_signature(path, signature, findings)
        return
    if kind != "function":
        findings.append(error(path, "signature.kind must be function or object"))
        return
    for language in ("java", "python"):
        language_signature = signature.get(language)
        if not isinstance(language_signature, dict):
            findings.append(error(path, f"signature.{language} is required"))
            continue
        for field in ("className", "methodName", "returnType"):
            if not require_text(language_signature.get(field)):
                findings.append(error(path, f"signature.{language}.{field} is required"))
        method_name = language_signature.get("methodName")
        if require_text(method_name) and not is_safe_identifier(method_name):
            findings.append(error(path, f"signature.{language}.methodName must be a safe identifier"))
        return_types = SUPPORTED_JAVA_RETURN_TYPES if language == "java" else SUPPORTED_PYTHON_RETURN_TYPES
        parameter_types = SUPPORTED_JAVA_PARAMETER_TYPES if language == "java" else SUPPORTED_PYTHON_PARAMETER_TYPES
        if language_signature.get("returnType") not in return_types:
            findings.append(error(path, f"signature.{language}.returnType is not supported by generated drivers"))
        if language_signature.get("className") != "Solution":
            findings.append(error(path, f"signature.{language}.className must be Solution"))
        if language == "python" and contains_python_39_builtin_generic(language_signature):
            findings.append(error(path, "signature.python must use Python 3.8-compatible typing names such as List[int]"))
        parameters = language_signature.get("parameters")
        if not isinstance(parameters, list):
            findings.append(error(path, f"signature.{language}.parameters must be a list"))
        else:
            for parameter in parameters:
                if not isinstance(parameter, dict):
                    findings.append(error(path, f"signature.{language}.parameters entries must be objects"))
                    continue
                if not require_text(parameter.get("name")) or not require_text(parameter.get("type")):
                    findings.append(error(path, f"signature.{language}.parameters entries require name and type"))
                elif not is_safe_identifier(parameter.get("name")):
                    findings.append(error(path, f"signature.{language}.parameters name must be a safe identifier"))
                if parameter.get("type") not in parameter_types:
                    findings.append(error(path, f"signature.{language}.parameters type is not supported by generated drivers"))
                if language == "python" and contains_python_39_builtin_generic(parameter):
                    findings.append(error(path, "signature.python parameters must use Python 3.8-compatible typing names"))
    validate_signature_parity(path, signature, findings)


def validate_custom_types(path: Path, signature: dict[str, Any], findings: list[Finding]) -> None:
    custom_types = signature.get("customTypes")
    uses_node = function_signature_uses_node(signature)
    if custom_types is None:
        if uses_node:
            findings.append(error(path, "signature.customTypes.Node is required when generated drivers use Node"))
        return
    if not isinstance(custom_types, dict):
        findings.append(error(path, "signature.customTypes must be an object"))
        return
    unexpected = sorted(set(custom_types) - {"Node"})
    for key in unexpected:
        findings.append(error(path, f"signature.customTypes.{key} is not supported"))
    node_kind = custom_types.get("Node")
    if node_kind not in SUPPORTED_CUSTOM_NODE_TYPES:
        findings.append(error(path, f"signature.customTypes.Node must be one of {sorted(SUPPORTED_CUSTOM_NODE_TYPES)}"))
    if not uses_node:
        findings.append(error(path, "signature.customTypes.Node is only allowed when generated drivers use Node"))
    if node_kind == "quad-tree" and function_signature_has_node_parameter(signature):
        findings.append(error(path, "signature.customTypes.Node quad-tree currently supports Node returns only"))


def function_signature_uses_node(signature: dict[str, Any]) -> bool:
    def language_uses_node(language_signature: Any, node_type: str) -> bool:
        if not isinstance(language_signature, dict):
            return False
        if language_signature.get("returnType") == node_type:
            return True
        return any(
            isinstance(parameter, dict) and parameter.get("type") == node_type
            for parameter in language_signature.get("parameters", [])
        )

    if language_uses_node(signature.get("java"), "Node") or language_uses_node(signature.get("python"), "Optional[Node]"):
        return True
    if signature.get("kind") != "object":
        return False

    def object_language_uses_node(language_signature: Any, node_type: str) -> bool:
        if not isinstance(language_signature, dict):
            return False
        constructor = language_signature.get("constructor")
        if isinstance(constructor, dict):
            if any(
                isinstance(parameter, dict) and parameter.get("type") == node_type
                for parameter in constructor.get("parameters", [])
            ):
                return True
        for method in language_signature.get("methods", []):
            if not isinstance(method, dict):
                continue
            if method.get("returnType") == node_type:
                return True
            if any(
                isinstance(parameter, dict) and parameter.get("type") == node_type
                for parameter in method.get("parameters", [])
            ):
                return True
        return False

    return object_language_uses_node(signature.get("java"), "Node") or object_language_uses_node(signature.get("python"), "Optional[Node]")


def function_signature_has_node_parameter(signature: dict[str, Any]) -> bool:
    def language_has_node_parameter(language_signature: Any, node_type: str) -> bool:
        if not isinstance(language_signature, dict):
            return False
        return any(
            isinstance(parameter, dict) and parameter.get("type") == node_type
            for parameter in language_signature.get("parameters", [])
        )

    return language_has_node_parameter(signature.get("java"), "Node") or language_has_node_parameter(
        signature.get("python"),
        "Optional[Node]",
    )


def signature_custom_node_kind(signature: Any) -> Any:
    if not isinstance(signature, dict):
        return None
    custom_types = signature.get("customTypes")
    if not isinstance(custom_types, dict):
        return None
    return custom_types.get("Node")


def validate_object_signature(path: Path, signature: dict[str, Any], findings: list[Finding]) -> None:
    for language in ("java", "python"):
        language_signature = signature.get(language)
        if not isinstance(language_signature, dict):
            findings.append(error(path, f"signature.{language} is required"))
            continue
        class_name = language_signature.get("className")
        if not require_text(class_name):
            findings.append(error(path, f"signature.{language}.className is required"))
        elif not is_safe_identifier(class_name):
            findings.append(error(path, f"signature.{language}.className must be a safe identifier"))

        constructor = language_signature.get("constructor")
        if not isinstance(constructor, dict):
            findings.append(error(path, f"signature.{language}.constructor is required"))
        else:
            validate_parameter_list(
                path,
                constructor.get("parameters"),
                language,
                f"signature.{language}.constructor.parameters",
                findings,
            )

        methods = language_signature.get("methods")
        if not isinstance(methods, list) or not methods:
            findings.append(error(path, f"signature.{language}.methods must be a non-empty list"))
            continue
        seen_methods: set[str] = set()
        for method in methods:
            if not isinstance(method, dict):
                findings.append(error(path, f"signature.{language}.methods entries must be objects"))
                continue
            method_name = method.get("name")
            if not require_text(method_name):
                findings.append(error(path, f"signature.{language}.methods entries require name"))
            elif not is_safe_identifier(method_name):
                findings.append(error(path, f"signature.{language}.methods name must be a safe identifier"))
            elif method_name in seen_methods:
                findings.append(error(path, f"duplicate object method {method_name}"))
            else:
                seen_methods.add(method_name)

            return_types = SUPPORTED_JAVA_RETURN_TYPES if language == "java" else SUPPORTED_PYTHON_RETURN_TYPES
            if method.get("returnType") not in return_types:
                findings.append(error(path, f"signature.{language}.methods returnType is not supported by generated drivers"))
            if language == "python" and contains_python_39_builtin_generic({"returnType": method.get("returnType")}):
                findings.append(error(path, "signature.python methods must use Python 3.8-compatible typing names"))
            validate_parameter_list(
                path,
                method.get("parameters"),
                language,
                f"signature.{language}.methods.{method_name}.parameters",
                findings,
            )
    validate_object_signature_parity(path, signature, findings)


def validate_parameter_list(
    path: Path,
    parameters: Any,
    language: str,
    label: str,
    findings: list[Finding],
) -> None:
    parameter_types = SUPPORTED_JAVA_PARAMETER_TYPES if language == "java" else SUPPORTED_PYTHON_PARAMETER_TYPES
    if not isinstance(parameters, list):
        findings.append(error(path, f"{label} must be a list"))
        return
    seen_names: set[str] = set()
    for parameter in parameters:
        if not isinstance(parameter, dict):
            findings.append(error(path, f"{label} entries must be objects"))
            continue
        name = parameter.get("name")
        type_name = parameter.get("type")
        if not require_text(name) or not require_text(type_name):
            findings.append(error(path, f"{label} entries require name and type"))
        elif not is_safe_identifier(name):
            findings.append(error(path, f"{label} name must be a safe identifier"))
        elif name in seen_names:
            findings.append(error(path, f"duplicate parameter {name}"))
        else:
            seen_names.add(name)
        if type_name not in parameter_types:
            findings.append(error(path, f"{label} type is not supported by generated drivers"))
        if language == "python" and contains_python_39_builtin_generic(parameter):
            findings.append(error(path, "signature.python parameters must use Python 3.8-compatible typing names"))


def validate_object_signature_parity(path: Path, signature: dict[str, Any], findings: list[Finding]) -> None:
    java_signature = signature.get("java")
    python_signature = signature.get("python")
    if not isinstance(java_signature, dict) or not isinstance(python_signature, dict):
        return
    if java_signature.get("className") != python_signature.get("className"):
        findings.append(error(path, "object signature java/python className must match"))
    validate_object_parameters_parity(
        path,
        java_signature.get("constructor", {}).get("parameters") if isinstance(java_signature.get("constructor"), dict) else None,
        python_signature.get("constructor", {}).get("parameters") if isinstance(python_signature.get("constructor"), dict) else None,
        "constructor",
        findings,
    )
    java_methods = java_signature.get("methods")
    python_methods = python_signature.get("methods")
    if not isinstance(java_methods, list) or not isinstance(python_methods, list):
        return
    java_method_names = [method.get("name") for method in java_methods if isinstance(method, dict)]
    python_method_names = [method.get("name") for method in python_methods if isinstance(method, dict)]
    if java_method_names != python_method_names:
        findings.append(error(path, "object signature java/python method names must match"))
        return
    for java_method, python_method in zip(java_methods, python_methods):
        if not isinstance(java_method, dict) or not isinstance(python_method, dict):
            continue
        if JAVA_TO_PYTHON_TYPES.get(java_method.get("returnType")) != python_method.get("returnType"):
            findings.append(error(path, "object signature java/python method return types must be compatible"))
        validate_object_parameters_parity(
            path,
            java_method.get("parameters"),
            python_method.get("parameters"),
            f"method {java_method.get('name')}",
            findings,
        )


def validate_object_parameters_parity(
    path: Path,
    java_parameters: Any,
    python_parameters: Any,
    label: str,
    findings: list[Finding],
) -> None:
    if not isinstance(java_parameters, list) or not isinstance(python_parameters, list):
        return
    java_names = [parameter.get("name") for parameter in java_parameters if isinstance(parameter, dict)]
    python_names = [parameter.get("name") for parameter in python_parameters if isinstance(parameter, dict)]
    if java_names != python_names:
        findings.append(error(path, f"object signature java/python {label} parameter names must match"))
    java_types = [parameter.get("type") for parameter in java_parameters if isinstance(parameter, dict)]
    python_types = [parameter.get("type") for parameter in python_parameters if isinstance(parameter, dict)]
    if len(java_types) != len(python_types):
        findings.append(error(path, f"object signature java/python {label} parameter arity must match"))
        return
    for java_type, python_type in zip(java_types, python_types):
        if JAVA_TO_PYTHON_TYPES.get(java_type) != python_type:
            findings.append(error(path, f"object signature java/python {label} parameter types must be compatible"))


def validate_problem_leetcode_metadata(
    path: Path,
    problem: dict[str, Any],
    source_index: dict[str, dict[str, dict[str, Any]]],
    findings: list[Finding],
) -> None:
    problem_id = problem.get("id")
    leetcode = problem.get("leetcode")
    if not isinstance(problem_id, str) or not isinstance(leetcode, dict):
        return
    source_items = [
        items[problem_id]
        for items in source_index.values()
        if problem_id in items
    ]
    if not source_items:
        return
    first = source_items[0]
    for source_key in ("sourceId", "titleSlug", "sourceUrl", "paidOnly"):
        known_values = [item[source_key] for item in source_items if source_key in item]
        if len({json.dumps(value, sort_keys=True) for value in known_values}) > 1:
            findings.append(error(path, f"source manifests disagree on LeetCode {source_key} metadata"))
    expected = {
        "frontendId": str(first.get("sourceId")),
        "titleSlug": first.get("titleSlug"),
        "url": first.get("sourceUrl"),
    }
    known_paid_values = [item["paidOnly"] for item in source_items if isinstance(item.get("paidOnly"), bool)]
    if known_paid_values:
        expected["paidOnly"] = known_paid_values[0]
    for key, expected_value in expected.items():
        if leetcode.get(key) != expected_value:
            findings.append(error(path, f"problem.json.leetcode.{key} must match source manifest metadata"))
    if not known_paid_values and "paidOnly" in leetcode:
        findings.append(error(path, "problem.json.leetcode.paidOnly must be omitted when source manifests do not know access status"))


def validate_signature_parity(path: Path, signature: dict[str, Any], findings: list[Finding]) -> None:
    java_signature = signature.get("java")
    python_signature = signature.get("python")
    if not isinstance(java_signature, dict) or not isinstance(python_signature, dict):
        return

    if JAVA_TO_PYTHON_TYPES.get(java_signature.get("returnType")) != python_signature.get("returnType"):
        findings.append(error(path, "signature java/python return types must be compatible for generated drivers"))

    java_parameters = java_signature.get("parameters")
    python_parameters = python_signature.get("parameters")
    if not isinstance(java_parameters, list) or not isinstance(python_parameters, list):
        return
    java_names = [
        parameter.get("name")
        for parameter in java_parameters
        if isinstance(parameter, dict) and require_text(parameter.get("name"))
    ]
    python_names = [
        parameter.get("name")
        for parameter in python_parameters
        if isinstance(parameter, dict) and require_text(parameter.get("name"))
    ]
    if java_names != python_names:
        findings.append(error(path, "signature java/python parameter names must match for generated drivers"))

    java_types = [
        parameter.get("type")
        for parameter in java_parameters
        if isinstance(parameter, dict) and require_text(parameter.get("type"))
    ]
    python_types = [
        parameter.get("type")
        for parameter in python_parameters
        if isinstance(parameter, dict) and require_text(parameter.get("type"))
    ]
    if len(java_types) != len(python_types):
        findings.append(error(path, "signature java/python parameter arity must match for generated drivers"))
        return
    for java_type, python_type in zip(java_types, python_types):
        if JAVA_TO_PYTHON_TYPES.get(java_type) != python_type:
            findings.append(error(path, "signature java/python parameter types must be compatible for generated drivers"))


def contains_python_39_builtin_generic(payload: dict[str, Any]) -> bool:
    values = [payload.get("returnType"), payload.get("type")]
    return any(isinstance(value, str) and PYTHON_BUILTIN_GENERIC_PATTERN.search(value) for value in values)


def python_source_uses_builtin_generics_without_future(text: str) -> bool:
    return bool(PYTHON_BUILTIN_GENERIC_PATTERN.search(text)) and not has_effective_future_annotations_import(text)


def has_effective_future_annotations_import(text: str) -> bool:
    try:
        module = ast.parse(text)
    except SyntaxError:
        return False

    statements = module.body
    index = 0
    if statements and isinstance(statements[0], ast.Expr):
        value = statements[0].value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            index = 1

    while index < len(statements):
        statement = statements[index]
        if not isinstance(statement, ast.ImportFrom) or statement.module != "__future__":
            return False
        if any(alias.name == "annotations" for alias in statement.names):
            return True
        index += 1

    return False


def is_safe_identifier(value: Any) -> bool:
    if not isinstance(value, str) or not SAFE_IDENTIFIER_PATTERN.fullmatch(value):
        return False
    return not keyword.iskeyword(value) and value not in JAVA_RESERVED_WORDS


def validate_clean_room_provenance(path: Path, problem: dict[str, Any], findings: list[Finding]) -> None:
    provenance = problem.get("provenance")
    if not isinstance(provenance, dict):
        findings.append(error(path, "completed problem must define provenance"))
        return
    expected = {
        "sourceUse": "metadata-only",
        "problemSummary": REPO_AUTHORED,
        "examples": REPO_AUTHORED,
        "cases": REPO_AUTHORED,
    }
    for key, value in expected.items():
        if provenance.get(key) != value:
            findings.append(error(path, f"provenance.{key} must be {value}"))


def validate_clean_room_review(problem_dir: Path, problem: dict[str, Any], findings: list[Finding]) -> None:
    path = problem_dir / "problem.json"
    review = problem.get("cleanRoomReview")
    if not isinstance(review, dict):
        findings.append(error(path, "completed problem must define cleanRoomReview"))
        return
    if not require_text(review.get("reviewer")):
        findings.append(error(path, "cleanRoomReview.reviewer is required"))
    if not is_iso_date(review.get("reviewedAt")):
        findings.append(error(path, "cleanRoomReview.reviewedAt must be an ISO date"))
    if review.get("verdict") != REQUIRED_CLEAN_ROOM_VERDICT:
        findings.append(error(path, f"cleanRoomReview.verdict must be {REQUIRED_CLEAN_ROOM_VERDICT}"))
    scope = review.get("scope")
    if not isinstance(scope, list) or not REQUIRED_CLEAN_ROOM_SCOPE.issubset(set(scope)):
        findings.append(error(path, "cleanRoomReview.scope must include problem.json, README.md, cases.json, and solutions.json"))

    for relative, reviewed_path in clean_room_review_paths(problem_dir, findings):
        if not reviewed_path.is_file():
            findings.append(error(reviewed_path, f"cleanRoomReview.scope includes missing reviewed file {relative}"))
            continue
        text = reviewed_path.read_text(encoding="utf-8")
        if text_reuses_blocked_source_example(text):
            findings.append(error(reviewed_path, "content appears to reuse a blocked source example"))


def clean_room_review_paths(problem_dir: Path, findings: list[Finding]) -> list[tuple[str, Path]]:
    paths = [
        ("problem.json", problem_dir / "problem.json"),
        ("README.md", problem_dir / "README.md"),
        ("cases.json", problem_dir / "cases.json"),
        ("solutions.json", problem_dir / "solutions.json"),
    ]
    try:
        payload = json.loads((problem_dir / "solutions.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return paths
    if not isinstance(payload, dict):
        return paths
    for solution in payload.get("solutions", []):
        if not isinstance(solution, dict):
            continue
        for key in ("javaPath", "pythonPath"):
            relative = solution.get(key)
            if isinstance(relative, str):
                language = "java" if key == "javaPath" else "python"
                if path_contains_symlink(problem_dir / relative, problem_dir):
                    findings.append(error(problem_dir / relative, f"{key} must not be a symlink"))
                    continue
                resolved, message = resolve_solution_path(problem_dir, relative, language)
                if message is not None or resolved is None:
                    findings.append(error(problem_dir / "solutions.json", f"{key} {message}"))
                    continue
                paths.append((relative, resolved))
    return paths


def validate_validation_receipt(path: Path, problem: dict[str, Any], findings: list[Finding]) -> None:
    validation = problem.get("validation")
    if not isinstance(validation, dict):
        findings.append(error(path, "completed problem must define validation receipt"))
        return
    validate_allowed_keys(path, validation, ALLOWED_VALIDATION_KEYS, "problem.json.validation", findings)
    if not is_iso_date(validation.get("validatedAt")):
        findings.append(error(path, "validation.validatedAt must be an ISO date"))

    checks = validation.get("checks")
    if not isinstance(checks, list) or not checks:
        findings.append(error(path, "validation.checks must be a non-empty list"))
        return

    seen_checks: dict[str, dict[str, Any]] = {}
    for index, check in enumerate(checks, start=1):
        if not isinstance(check, dict):
            findings.append(error(path, f"validation.checks[{index}] must be an object"))
            continue
        validate_allowed_keys(path, check, ALLOWED_VALIDATION_CHECK_KEYS, f"problem.json.validation.checks[{index}]", findings)
        name = check.get("name")
        if not require_text(name):
            findings.append(error(path, f"validation.checks[{index}].name is required"))
        elif name in seen_checks:
            findings.append(error(path, f"duplicate validation check {name}"))
        else:
            seen_checks[name] = check
        status = check.get("status")
        if status not in VALIDATION_CHECK_STATUSES:
            findings.append(error(path, f"validation.checks[{index}].status must be one of {sorted(VALIDATION_CHECK_STATUSES)}"))
        if not require_text(check.get("command")):
            findings.append(error(path, f"validation.checks[{index}].command is required"))
        language = check.get("language")
        if language is not None and language not in VALIDATION_CHECK_LANGUAGES:
            findings.append(error(path, f"validation.checks[{index}].language must be java or python"))
        if status == "blocked" and not require_text(check.get("reason")):
            findings.append(error(path, f"validation.checks[{index}].reason is required when status is blocked"))
        if status == "passed" and "reason" in check:
            findings.append(error(path, f"validation.checks[{index}].reason is only allowed for blocked checks"))

        if require_text(name):
            contract = VALIDATION_CHECK_CONTRACTS.get(name)
            if contract is None:
                findings.append(error(path, f"unexpected validation check {name}"))
            else:
                expected_command = contract["command"]
                if check.get("command") != expected_command:
                    findings.append(error(path, f"validation check {name} command must be {expected_command}"))
                expected_language = contract["language"]
                if expected_language is None:
                    if "language" in check:
                        findings.append(error(path, f"validation check {name} must not define language"))
                elif check.get("language") != expected_language:
                    findings.append(error(path, f"validation check {name} language must be {expected_language}"))

    for required_name, contract in VALIDATION_CHECK_CONTRACTS.items():
        check = seen_checks.get(required_name)
        if check is None:
            findings.append(error(path, f"missing validation check {required_name}"))
            continue
        allowed_statuses = contract["statuses"]
        if check.get("status") not in allowed_statuses:
            if allowed_statuses == {"passed"}:
                findings.append(error(path, f"validation check {required_name} must be passed"))
            else:
                findings.append(error(path, f"validation check {required_name} status must be one of {sorted(allowed_statuses)}"))
    java_check = seen_checks.get("java-drivers")
    if isinstance(java_check, dict) and java_check.get("status") == "blocked":
        reason = java_check.get("reason")
        expected_reason = VALIDATION_CHECK_CONTRACTS["java-drivers"]["blockedReason"]
        if reason != expected_reason:
            findings.append(error(path, f"blocked java-drivers validation check must use reason {expected_reason}"))


def path_contains_symlink(path: Path, root: Path) -> bool:
    try:
        relative_parts = path.relative_to(root).parts
    except ValueError:
        return False
    current = root
    for part in relative_parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def validate_cases(path: Path, cases_payload: dict[str, Any], problem: dict[str, Any], findings: list[Finding]) -> None:
    if cases_payload.get("source") != REPO_AUTHORED:
        findings.append(error(path, f"cases source must be {REPO_AUTHORED}"))

    matcher = cases_payload.get("matcher", {})
    matcher_type = matcher.get("type", "exact") if isinstance(matcher, dict) else None
    if matcher_type not in SUPPORTED_MATCHERS:
        findings.append(error(path, f"unsupported matcher {matcher_type}"))

    cases = cases_payload.get("cases")
    if not isinstance(cases, list) or not cases:
        findings.append(error(path, "completed problem must define at least one test case"))
        return

    signature = problem.get("signature", {})
    object_signature = isinstance(signature, dict) and signature.get("kind") == "object"
    python_signature = signature.get("python", {}) if isinstance(signature, dict) else {}
    java_signature = signature.get("java", {}) if isinstance(signature, dict) else {}
    if object_signature:
        validate_object_cases(path, cases, matcher if isinstance(matcher, dict) else {}, matcher_type, java_signature, python_signature, findings)
        return
    if matcher_type == "object-one-of":
        findings.append(error(path, "object-one-of matcher requires object operation cases"))
    parameters = python_signature.get("parameters", []) if isinstance(python_signature, dict) else []
    java_parameters = java_signature.get("parameters", []) if isinstance(java_signature, dict) else []
    parameter_names = [
        parameter.get("name")
        for parameter in parameters
        if isinstance(parameter, dict) and require_text(parameter.get("name"))
    ]
    java_parameter_types = {
        parameter.get("name"): parameter.get("type")
        for parameter in java_parameters
        if isinstance(parameter, dict) and require_text(parameter.get("name"))
    }
    python_parameter_types = {
        parameter.get("name"): parameter.get("type")
        for parameter in parameters
        if isinstance(parameter, dict) and require_text(parameter.get("name"))
    }
    void_return = (
        isinstance(java_signature, dict)
        and isinstance(python_signature, dict)
        and java_signature.get("returnType") == "void"
        and python_signature.get("returnType") == "None"
    )
    tree_return = (
        isinstance(java_signature, dict)
        and isinstance(python_signature, dict)
        and java_signature.get("returnType") == "TreeNode"
        and python_signature.get("returnType") == "Optional[TreeNode]"
    )
    floating_return = (
        isinstance(java_signature, dict)
        and isinstance(python_signature, dict)
        and (
            (
                java_signature.get("returnType") in {"double", "float"}
                and python_signature.get("returnType") == "float"
            )
            or (
                java_signature.get("returnType") in {"double[]", "List<Double>"}
                and python_signature.get("returnType") == "List[float]"
            )
        )
    )
    if floating_return and matcher_type != "float-tolerance":
        findings.append(error(path, "floating return signatures require float-tolerance matcher"))
    if matcher_type == "balanced-bst-from-sorted-array":
        if not tree_return:
            findings.append(error(path, "balanced-bst-from-sorted-array matcher requires a TreeNode return signature"))
        if java_parameter_types.get("nums") != "int[]" or python_parameter_types.get("nums") != "List[int]":
            findings.append(error(path, "balanced-bst-from-sorted-array matcher requires a nums array/list parameter"))
    if matcher_type == "unordered-list-of-lists":
        if not (
            isinstance(java_signature, dict)
            and isinstance(python_signature, dict)
            and (
                (
                    java_signature.get("returnType") == "List<List<Integer>>"
                    and python_signature.get("returnType") == "List[List[int]]"
                )
                or (
                    java_signature.get("returnType") == "int[][]"
                    and python_signature.get("returnType") == "List[List[int]]"
                )
                or (
                    java_signature.get("returnType") == "List<List<String>>"
                    and python_signature.get("returnType") == "List[List[str]]"
                )
            )
        ):
            findings.append(error(path, "unordered-list-of-lists matcher requires a nested list return signature"))
    if matcher_type == "unordered-list":
        if not (
            isinstance(java_signature, dict)
            and isinstance(python_signature, dict)
            and (
                (
                    java_signature.get("returnType") == "List<String>"
                    and python_signature.get("returnType") == "List[str]"
                )
                or (
                    java_signature.get("returnType") == "List<Integer>"
                    and python_signature.get("returnType") == "List[int]"
                )
            )
        ):
            findings.append(error(path, "unordered-list matcher requires a flat string or integer list return signature"))
    if matcher_type == "unordered-tree-list":
        if not (
            isinstance(java_signature, dict)
            and isinstance(python_signature, dict)
            and java_signature.get("returnType") == "List<TreeNode>"
            and python_signature.get("returnType") == "List[Optional[TreeNode]]"
        ):
            findings.append(error(path, "unordered-tree-list matcher requires a List<TreeNode> return signature"))
    if matcher_type == "valid-topological-order":
        if not (
            isinstance(java_signature, dict)
            and isinstance(python_signature, dict)
            and java_signature.get("returnType") == "int[]"
            and python_signature.get("returnType") == "List[int]"
            and java_parameter_types.get("numCourses") == "int"
            and python_parameter_types.get("numCourses") == "int"
            and java_parameter_types.get("prerequisites") == "int[][]"
            and python_parameter_types.get("prerequisites") == "List[List[int]]"
        ):
            findings.append(error(path, "valid-topological-order matcher requires Course Schedule II signatures"))
    if matcher_type == "float-tolerance":
        tolerance = matcher.get("tolerance") if isinstance(matcher, dict) else None
        if not is_finite_number(tolerance) or tolerance <= 0:
            findings.append(error(path, "float-tolerance matcher requires a positive finite tolerance"))
        if not (
            isinstance(java_signature, dict)
            and isinstance(python_signature, dict)
            and (
                (
                    java_signature.get("returnType") in {"double", "float"}
                    and python_signature.get("returnType") == "float"
                )
                or (
                    java_signature.get("returnType") in {"double[]", "List<Double>"}
                    and python_signature.get("returnType") == "List[float]"
                )
            )
        ):
            findings.append(error(path, "float-tolerance matcher requires a floating return signature"))

    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            findings.append(error(path, f"case {index} must be an object"))
            continue
        validate_allowed_keys(path, case, ALLOWED_CASE_KEYS, f"case {index}", findings)
        if not require_text(case.get("name")):
            findings.append(error(path, f"case {index} name is required"))
        inputs = case.get("input")
        if not isinstance(inputs, dict):
            findings.append(error(path, f"case {index} input must be an object"))
            continue
        for parameter_name in parameter_names:
            if parameter_name not in inputs:
                findings.append(error(path, f"case {index} missing input {parameter_name}"))
            elif not value_matches_parameter_type(
                inputs.get(parameter_name),
                java_parameter_types.get(parameter_name),
                python_parameter_types.get(parameter_name),
                signature_custom_node_kind(signature),
            ):
                findings.append(
                    error(
                        path,
                        f"case {index} input.{parameter_name} "
                        f"must match {java_parameter_types.get(parameter_name)}/{python_parameter_types.get(parameter_name)}",
                    )
                )
        validate_tree_node_references(
            path,
            index,
            inputs,
            parameter_names,
            java_parameter_types,
            python_parameter_types,
            findings,
        )
        extra_input_keys = sorted(set(inputs) - set(parameter_names))
        for input_key in extra_input_keys:
            findings.append(error(path, f"case {index} input contains unsupported key {input_key}"))
        if "expected" not in case:
            findings.append(error(path, f"case {index} expected is required"))
        elif void_return and case.get("expected") is not None:
            findings.append(error(path, f"case {index} expected must be null for void/None return signatures"))
        elif tree_return and case.get("expected") is None:
            findings.append(error(path, f"case {index} expected must use [] for an empty TreeNode result"))
        elif matcher_type == "exact" and not expected_matches_return_type(
            case.get("expected"),
            java_signature.get("returnType") if isinstance(java_signature, dict) else None,
            python_signature.get("returnType") if isinstance(python_signature, dict) else None,
            signature_custom_node_kind(signature),
        ):
            findings.append(
                error(
                    path,
                    f"case {index} expected must match "
                    f"{java_signature.get('returnType') if isinstance(java_signature, dict) else None}/"
                    f"{python_signature.get('returnType') if isinstance(python_signature, dict) else None}",
                )
            )
        elif matcher_type == "unordered-list-of-lists" and not expected_matches_unordered_nested_list_return(
            case.get("expected"),
            java_signature.get("returnType") if isinstance(java_signature, dict) else None,
            python_signature.get("returnType") if isinstance(python_signature, dict) else None,
        ):
            findings.append(error(path, f"case {index} expected must be a list of lists matching unordered-list-of-lists return type"))
        elif matcher_type == "unordered-list" and not expected_matches_unordered_list_return(
            case.get("expected"),
            java_signature.get("returnType") if isinstance(java_signature, dict) else None,
            python_signature.get("returnType") if isinstance(python_signature, dict) else None,
        ):
            findings.append(error(path, f"case {index} expected must be a flat list matching unordered-list return type"))
        elif matcher_type == "unordered-tree-list" and not expected_matches_unordered_tree_list_return(
            case.get("expected"),
            java_signature.get("returnType") if isinstance(java_signature, dict) else None,
            python_signature.get("returnType") if isinstance(python_signature, dict) else None,
        ):
            findings.append(error(path, f"case {index} expected must be a list of TreeNode level-order values"))
        elif matcher_type == "float-tolerance" and not expected_matches_float_tolerance_return(
            case.get("expected"),
            java_signature.get("returnType") if isinstance(java_signature, dict) else None,
            python_signature.get("returnType") if isinstance(python_signature, dict) else None,
        ):
            findings.append(error(path, f"case {index} expected must match float-tolerance return type"))
        elif matcher_type == "valid-topological-order" and not is_list_of_ints(case.get("expected")):
            findings.append(error(path, f"case {index} expected must be an integer list for valid-topological-order matcher"))
        if tree_return and is_tree_node_reference(case.get("expected")):
            validate_tree_node_reference(
                path,
                index,
                "expected",
                case.get("expected"),
                inputs,
                parameter_names,
                java_parameter_types,
                python_parameter_types,
                findings,
                require_prior=False,
            )
        if matcher_type == "valid-topological-order":
            validate_topological_order_case_input(path, index, inputs, findings)
        expected_mutations = case.get("expectedMutations")
        if void_return and expected_mutations is None:
            findings.append(error(path, f"case {index} expectedMutations is required for void/None return signatures"))
        if expected_mutations is not None:
            validate_expected_mutations(
                path,
                index,
                expected_mutations,
                parameter_names,
                java_parameter_types,
                python_parameter_types,
                findings,
                signature_custom_node_kind(signature),
            )
        linked_list_contract = case.get("linkedListContract")
        if linked_list_contract is not None:
            validate_linked_list_contract(
                path,
                index,
                linked_list_contract,
                inputs,
                parameter_names,
                java_parameter_types,
                python_parameter_types,
                java_signature.get("returnType") if isinstance(java_signature, dict) else None,
                python_signature.get("returnType") if isinstance(python_signature, dict) else None,
                findings,
            )
        if source_example_fingerprint_is_blocked(case):
            findings.append(error(path, f"case {index} appears to reuse a blocked source example"))


def validate_object_cases(
    path: Path,
    cases: list[Any],
    matcher: dict[str, Any],
    matcher_type: str | None,
    java_signature: Any,
    python_signature: Any,
    findings: list[Finding],
) -> None:
    if matcher_type not in {"exact", "float-tolerance", "object-one-of"}:
        findings.append(error(path, "object operation cases require exact, float-tolerance, or object-one-of matcher"))
    if not isinstance(java_signature, dict) or not isinstance(python_signature, dict):
        return
    java_methods = object_methods_by_name(java_signature)
    python_methods = object_methods_by_name(python_signature)
    floating_method_exists = any(
        is_floating_return(method.get("returnType"), python_methods.get(name, {}).get("returnType"))
        for name, method in java_methods.items()
    )
    if floating_method_exists and matcher_type != "float-tolerance":
        findings.append(error(path, "floating object operation returns require float-tolerance matcher"))
    if matcher_type == "float-tolerance":
        tolerance = matcher.get("tolerance")
        if not is_finite_number(tolerance) or tolerance <= 0:
            findings.append(error(path, "float-tolerance matcher requires a positive finite tolerance"))
        if not floating_method_exists:
            findings.append(error(path, "float-tolerance matcher requires a floating object operation return"))

    for case_index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            findings.append(error(path, f"case {case_index} must be an object"))
            continue
        validate_allowed_keys(path, case, ALLOWED_OBJECT_CASE_KEYS, f"case {case_index}", findings)
        if not require_text(case.get("name")):
            findings.append(error(path, f"case {case_index} name is required"))
        operations = case.get("operations")
        if not isinstance(operations, list) or not operations:
            findings.append(error(path, f"case {case_index} operations must be a non-empty list"))
            continue
        for operation_index, operation in enumerate(operations, start=1):
            if not isinstance(operation, dict):
                findings.append(error(path, f"case {case_index} operation {operation_index} must be an object"))
                continue
            validate_allowed_keys(path, operation, ALLOWED_OBJECT_OPERATION_KEYS, f"case {case_index} operation {operation_index}", findings)
            if "expected" not in operation:
                findings.append(error(path, f"case {case_index} operation {operation_index} expected is required"))
            operation_type = operation.get("type")
            if operation_type == "constructor":
                if operation_index != 1:
                    findings.append(error(path, f"case {case_index} constructor operation must be first"))
                if "method" in operation:
                    findings.append(error(path, f"case {case_index} constructor operation must not define method"))
                validate_object_operation_inputs(
                    path,
                    case_index,
                    operation_index,
                    operation.get("input"),
                    java_signature.get("constructor", {}).get("parameters") if isinstance(java_signature.get("constructor"), dict) else [],
                    python_signature.get("constructor", {}).get("parameters") if isinstance(python_signature.get("constructor"), dict) else [],
                    findings,
                )
                if operation.get("expected") is not None:
                    findings.append(error(path, f"case {case_index} constructor operation expected must be null"))
            elif operation_type == "call":
                method_name = operation.get("method")
                if not require_text(method_name):
                    findings.append(error(path, f"case {case_index} operation {operation_index} method is required"))
                    continue
                java_method = java_methods.get(method_name)
                python_method = python_methods.get(method_name)
                if java_method is None or python_method is None:
                    findings.append(error(path, f"case {case_index} operation {method_name} is not defined by object signature"))
                    continue
                validate_object_operation_inputs(
                    path,
                    case_index,
                    operation_index,
                    operation.get("input"),
                    java_method.get("parameters"),
                    python_method.get("parameters"),
                    findings,
                )
                if matcher_type == "object-one-of" and isinstance(operation.get("expected"), dict):
                    expected_valid = expected_matches_object_one_of(
                        operation.get("expected"),
                        java_method.get("returnType"),
                        python_method.get("returnType"),
                    )
                else:
                    expected_valid = expected_matches_return_type(
                        operation.get("expected"),
                        java_method.get("returnType"),
                        python_method.get("returnType"),
                    )
                if not expected_valid:
                    findings.append(error(path, f"case {case_index} operation {operation_index} expected must match method return type"))
            else:
                findings.append(error(path, f"case {case_index} operation {operation_index} type must be constructor or call"))
        first = operations[0] if operations and isinstance(operations[0], dict) else None
        if not isinstance(first, dict) or first.get("type") != "constructor":
            findings.append(error(path, f"case {case_index} first operation must be constructor"))
        if source_example_fingerprint_is_blocked(case):
            findings.append(error(path, f"case {case_index} appears to reuse a blocked source example"))


def object_methods_by_name(language_signature: dict[str, Any]) -> dict[str, dict[str, Any]]:
    methods = language_signature.get("methods")
    if not isinstance(methods, list):
        return {}
    return {
        method["name"]: method
        for method in methods
        if isinstance(method, dict) and require_text(method.get("name"))
    }


def validate_object_operation_inputs(
    path: Path,
    case_index: int,
    operation_index: int,
    inputs: Any,
    java_parameters: Any,
    python_parameters: Any,
    findings: list[Finding],
) -> None:
    if not isinstance(inputs, dict):
        findings.append(error(path, f"case {case_index} operation {operation_index} input must be an object"))
        return
    if not isinstance(java_parameters, list) or not isinstance(python_parameters, list):
        return
    parameter_names = [
        parameter.get("name")
        for parameter in python_parameters
        if isinstance(parameter, dict) and require_text(parameter.get("name"))
    ]
    java_types = {
        parameter.get("name"): parameter.get("type")
        for parameter in java_parameters
        if isinstance(parameter, dict) and require_text(parameter.get("name"))
    }
    python_types = {
        parameter.get("name"): parameter.get("type")
        for parameter in python_parameters
        if isinstance(parameter, dict) and require_text(parameter.get("name"))
    }
    for parameter_name in parameter_names:
        if parameter_name not in inputs:
            findings.append(error(path, f"case {case_index} operation {operation_index} missing input {parameter_name}"))
        elif not value_matches_parameter_type(
            inputs.get(parameter_name),
            java_types.get(parameter_name),
            python_types.get(parameter_name),
        ):
            findings.append(
                error(
                    path,
                    f"case {case_index} operation {operation_index} input.{parameter_name} "
                    f"must match {java_types.get(parameter_name)}/{python_types.get(parameter_name)}",
                )
            )
    for input_key in sorted(set(inputs) - set(parameter_names)):
        findings.append(error(path, f"case {case_index} operation {operation_index} input contains unsupported key {input_key}"))


def is_floating_return(java_return: Any, python_return: Any) -> bool:
    return (
        (java_return in {"double", "float"} and python_return == "float")
        or (java_return in {"double[]", "List<Double>"} and python_return == "List[float]")
    )


def value_matches_parameter_type(value: Any, java_type: Any, python_type: Any, custom_node_kind: Any = None) -> bool:
    if java_type == "Node" and python_type == "Optional[Node]":
        if custom_node_kind == "binary-tree-next":
            return is_tree_node_value(value)
        if custom_node_kind == "random-list":
            return is_random_list_value(value)
        if custom_node_kind == "graph":
            return is_graph_adjacency_value(value)
        if custom_node_kind == "quad-tree":
            return is_quad_tree_value(value)
        return False
    return value_matches_non_node_parameter_type(value, java_type, python_type)


def value_matches_non_node_parameter_type(value: Any, java_type: Any, python_type: Any) -> bool:
    if java_type == "int" and python_type == "int":
        return type(value) is int
    if java_type in {"double", "float"} and python_type == "float":
        return is_finite_number(value)
    if java_type == "char" and python_type == "str":
        return isinstance(value, str) and len(value) == 1
    if java_type == "boolean" and python_type == "bool":
        return isinstance(value, bool)
    if java_type == "String" and python_type == "str":
        return isinstance(value, str)
    if java_type == "int[]" and python_type == "List[int]":
        return is_list_of_ints(value)
    if java_type == "int[][]" and python_type == "List[List[int]]":
        return is_list_of_int_lists(value)
    if java_type == "int[][][]" and python_type == "List[List[List[int]]]":
        return is_list_of_int_list_lists(value)
    if java_type == "char[]" and python_type == "List[str]":
        return is_list_of_chars(value)
    if java_type == "char[][]" and python_type == "List[List[str]]":
        return is_char_grid(value)
    if java_type == "double[]" and python_type == "List[float]":
        return is_list_of_finite_numbers(value)
    if java_type == "String[]" and python_type == "List[str]":
        return is_list_of_strings(value)
    if java_type == "List<Integer>" and python_type == "List[int]":
        return is_list_of_ints(value)
    if java_type == "List<Double>" and python_type == "List[float]":
        return is_list_of_finite_numbers(value)
    if java_type == "List<String>" and python_type == "List[str]":
        return is_list_of_strings(value)
    if java_type == "List<List<Integer>>" and python_type == "List[List[int]]":
        return is_list_of_int_lists(value)
    if java_type == "List<List<String>>" and python_type == "List[List[str]]":
        return is_list_of_string_lists(value)
    if java_type == "ListNode" and python_type == "Optional[ListNode]":
        return is_linked_list_input(value)
    if java_type == "ListNode[]" and python_type == "List[Optional[ListNode]]":
        return is_list_of_linked_list_inputs(value)
    if java_type == "TreeNode" and python_type == "Optional[TreeNode]":
        return is_tree_node_input(value)
    return False


def expected_matches_return_type(value: Any, java_return: Any, python_return: Any, custom_node_kind: Any = None) -> bool:
    if java_return == "void" and python_return == "None":
        return value is None
    if java_return == "int" and python_return == "int":
        return type(value) is int
    if java_return == "boolean" and python_return == "bool":
        return isinstance(value, bool)
    if java_return == "String" and python_return == "str":
        return isinstance(value, str)
    if java_return in {"double", "float"} and python_return == "float":
        return is_finite_number(value)
    if java_return == "char" and python_return == "str":
        return isinstance(value, str) and len(value) == 1
    if java_return == "int[]" and python_return == "List[int]":
        return is_list_of_ints(value)
    if java_return == "int[][]" and python_return == "List[List[int]]":
        return is_list_of_int_lists(value)
    if java_return == "char[]" and python_return == "List[str]":
        return is_list_of_chars(value)
    if java_return == "char[][]" and python_return == "List[List[str]]":
        return is_char_grid(value)
    if java_return == "String[]" and python_return == "List[str]":
        return is_list_of_strings(value)
    if java_return == "double[]" and python_return == "List[float]":
        return is_list_of_finite_numbers(value)
    if java_return == "List<Integer>" and python_return == "List[int]":
        return is_list_of_ints(value)
    if java_return == "List<String>" and python_return == "List[str]":
        return is_list_of_strings(value)
    if java_return in {"double[]", "List<Double>"} and python_return == "List[float]":
        return is_list_of_finite_numbers(value)
    if java_return == "List<TreeNode>" and python_return == "List[Optional[TreeNode]]":
        return is_list_of_tree_node_values(value)
    if java_return == "List<List<Integer>>" and python_return == "List[List[int]]":
        return is_list_of_int_lists(value)
    if java_return == "List<List<String>>" and python_return == "List[List[str]]":
        return is_list_of_string_lists(value)
    if java_return == "ListNode" and python_return == "Optional[ListNode]":
        return value is None or is_list_of_ints(value)
    if java_return == "Node" and python_return == "Optional[Node]":
        if custom_node_kind == "binary-tree-next":
            return is_list_of_int_lists(value)
        if custom_node_kind == "random-list":
            return is_random_list_value(value)
        if custom_node_kind == "graph":
            return is_graph_adjacency_value(value)
        if custom_node_kind == "quad-tree":
            return is_quad_tree_value(value)
        return False
    if java_return == "TreeNode" and python_return == "Optional[TreeNode]":
        return is_tree_node_value(value) or is_tree_node_reference(value)
    return False


def expected_matches_object_one_of(value: Any, java_return: Any, python_return: Any) -> bool:
    if not isinstance(value, dict) or set(value) != {"oneOf"}:
        return False
    options = value.get("oneOf")
    if java_return == "int" and python_return == "int":
        return isinstance(options, list) and bool(options) and all(type(item) is int for item in options)
    return False


def is_list_of_ints(value: Any) -> bool:
    return isinstance(value, list) and all(type(item) is int for item in value)


def is_list_of_int_lists(value: Any) -> bool:
    return isinstance(value, list) and all(is_list_of_ints(row) for row in value)


def is_list_of_int_list_lists(value: Any) -> bool:
    return isinstance(value, list) and all(is_list_of_int_lists(row) for row in value)


def is_list_of_chars(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and len(item) == 1 for item in value)


def is_list_of_linked_list_inputs(value: Any) -> bool:
    return isinstance(value, list) and all(is_linked_list_input(item) for item in value)


def is_random_list_value(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    for row in value:
        if not isinstance(row, list) or len(row) != 2:
            return False
        node_value, random_index = row
        if type(node_value) is not int:
            return False
        if random_index is not None and (type(random_index) is not int or random_index < 0 or random_index >= len(value)):
            return False
    return True


def is_graph_adjacency_value(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    node_count = len(value)
    for row in value:
        if not isinstance(row, list):
            return False
        seen_neighbors: set[int] = set()
        for neighbor in row:
            if type(neighbor) is not int or neighbor < 1 or neighbor > node_count or neighbor in seen_neighbors:
                return False
            seen_neighbors.add(neighbor)
    if node_count == 0:
        return True
    reachable = {1}
    queue = [1]
    queue_index = 0
    while queue_index < len(queue):
        node = queue[queue_index]
        queue_index += 1
        for neighbor in value[node - 1]:
            if neighbor not in reachable:
                reachable.add(neighbor)
                queue.append(neighbor)
    if len(reachable) != node_count:
        return False
    return True


def is_quad_tree_value(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    required = {"val", "isLeaf", "topLeft", "topRight", "bottomLeft", "bottomRight"}
    if set(value) != required:
        return False
    if type(value.get("val")) is not bool or type(value.get("isLeaf")) is not bool:
        return False
    children = [value.get("topLeft"), value.get("topRight"), value.get("bottomLeft"), value.get("bottomRight")]
    if value["isLeaf"]:
        return all(child is None for child in children)
    return all(is_quad_tree_value(child) for child in children)


def is_linked_list_input(value: Any) -> bool:
    if value is None or is_list_of_ints(value):
        return True
    return is_cyclic_linked_list_input(value)


def is_cyclic_linked_list_input(value: Any) -> bool:
    if not isinstance(value, dict) or set(value) != {"values", "cycleTo"}:
        return False
    values = value.get("values")
    cycle_to = value.get("cycleTo")
    return is_list_of_ints(values) and type(cycle_to) is int and 0 <= cycle_to < len(values)


def linked_list_input_length(value: Any) -> int | None:
    if value is None:
        return 0
    if is_list_of_ints(value):
        return len(value)
    if isinstance(value, dict) and is_list_of_ints(value.get("values")):
        return len(value["values"])
    return None


def is_tree_node_input(value: Any) -> bool:
    return is_tree_node_value(value) or is_tree_node_reference(value)


def is_tree_node_value(value: Any) -> bool:
    if value is None:
        return True
    return tree_node_level_order_is_valid(value)


def is_list_of_tree_node_values(value: Any) -> bool:
    return isinstance(value, list) and all(is_tree_node_value(item) for item in value)


def tree_node_level_order_is_valid(value: Any) -> bool:
    if not isinstance(value, list) or not all(item is None or type(item) is int for item in value):
        return False
    if not value:
        return True
    if value[0] is None:
        return all(item is None for item in value[1:])
    queue_length = 1
    queue_index = 0
    value_index = 1
    while queue_index < queue_length and value_index < len(value):
        queue_index += 1
        if value_index < len(value):
            left_value = value[value_index]
            value_index += 1
            if left_value is not None:
                queue_length += 1
        if value_index < len(value):
            right_value = value[value_index]
            value_index += 1
            if right_value is not None:
                queue_length += 1
    return all(item is None for item in value[value_index:])


def is_tree_node_reference(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"from", "path"}
        and require_text(value.get("from"))
        and isinstance(value.get("path"), str)
        and all(char in {"L", "R"} for char in value.get("path", ""))
    )


def tree_node_path_exists(value: Any, path: str) -> bool:
    if value is None or value == [] or not isinstance(value, list) or value[0] is None:
        return False
    paths = {""}
    queue = [""]
    queue_index = 0
    value_index = 1
    while queue_index < len(queue) and value_index < len(value):
        current_path = queue[queue_index]
        queue_index += 1
        if value_index < len(value):
            left_value = value[value_index]
            value_index += 1
            if left_value is not None:
                left_path = current_path + "L"
                paths.add(left_path)
                queue.append(left_path)
        if value_index < len(value):
            right_value = value[value_index]
            value_index += 1
            if right_value is not None:
                right_path = current_path + "R"
                paths.add(right_path)
                queue.append(right_path)
    return path in paths


def validate_tree_node_references(
    path: Path,
    index: int,
    inputs: dict[str, Any],
    parameter_names: list[str],
    java_parameter_types: dict[str, Any],
    python_parameter_types: dict[str, Any],
    findings: list[Finding],
) -> None:
    for parameter_index, parameter_name in enumerate(parameter_names):
        value = inputs.get(parameter_name)
        if is_tree_node_reference(value):
            validate_tree_node_reference(
                path,
                index,
                f"input.{parameter_name}",
                value,
                inputs,
                parameter_names,
                java_parameter_types,
                python_parameter_types,
                findings,
                require_prior=True,
                current_parameter_index=parameter_index,
            )


def validate_tree_node_reference(
    path: Path,
    index: int,
    label: str,
    reference: Any,
    inputs: dict[str, Any],
    parameter_names: list[str],
    java_parameter_types: dict[str, Any],
    python_parameter_types: dict[str, Any],
    findings: list[Finding],
    *,
    require_prior: bool,
    current_parameter_index: int | None = None,
) -> None:
    if not is_tree_node_reference(reference):
        findings.append(error(path, f"case {index} {label} must be a TreeNode reference object"))
        return
    source_name = reference["from"]
    source_index = parameter_names.index(source_name) if source_name in parameter_names else -1
    if source_index < 0:
        findings.append(error(path, f"case {index} {label}.from must name a signature parameter"))
        return
    if require_prior and current_parameter_index is not None and source_index >= current_parameter_index:
        findings.append(error(path, f"case {index} {label}.from must reference an earlier TreeNode parameter"))
        return
    if not (
        java_parameter_types.get(source_name) == "TreeNode"
        and python_parameter_types.get(source_name) == "Optional[TreeNode]"
    ):
        findings.append(error(path, f"case {index} {label}.from must target a TreeNode parameter"))
        return
    source_value = inputs.get(source_name)
    if is_tree_node_reference(source_value):
        findings.append(error(path, f"case {index} {label}.from must target a concrete TreeNode input"))
        return
    if not tree_node_path_exists(source_value, reference["path"]):
        findings.append(error(path, f"case {index} {label}.path does not resolve to a TreeNode"))


def is_list_of_strings(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def is_list_of_string_lists(value: Any) -> bool:
    return isinstance(value, list) and all(is_list_of_strings(row) for row in value)


def is_char_grid(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(row, list) and all(isinstance(item, str) and len(item) == 1 for item in row)
        for row in value
    )


def is_finite_number(value: Any) -> bool:
    return type(value) in {int, float} and math.isfinite(float(value))


def is_list_of_finite_numbers(value: Any) -> bool:
    return isinstance(value, list) and all(is_finite_number(item) for item in value)


def expected_matches_unordered_nested_list_return(value: Any, java_return: Any, python_return: Any) -> bool:
    if java_return in {"int[][]", "List<List<Integer>>"} and python_return == "List[List[int]]":
        return is_list_of_int_lists(value)
    if java_return == "List<List<String>>" and python_return == "List[List[str]]":
        return is_list_of_string_lists(value)
    return False


def expected_matches_unordered_list_return(value: Any, java_return: Any, python_return: Any) -> bool:
    if not isinstance(value, list):
        return False
    if java_return == "List<String>" and python_return == "List[str]":
        return all(isinstance(item, str) for item in value)
    if java_return == "List<Integer>" and python_return == "List[int]":
        return all(type(item) is int for item in value)
    if java_return in {"double[]", "List<Double>"} and python_return == "List[float]":
        return is_list_of_finite_numbers(value)
    return False


def expected_matches_unordered_tree_list_return(value: Any, java_return: Any, python_return: Any) -> bool:
    if java_return == "List<TreeNode>" and python_return == "List[Optional[TreeNode]]":
        return is_list_of_tree_node_values(value)
    return False


def expected_matches_float_tolerance_return(value: Any, java_return: Any, python_return: Any) -> bool:
    if java_return in {"double", "float"} and python_return == "float":
        return is_finite_number(value)
    if java_return in {"double[]", "List<Double>"} and python_return == "List[float]":
        return is_list_of_finite_numbers(value)
    return False


def validate_topological_order_case_input(
    path: Path,
    index: int,
    inputs: dict[str, Any],
    findings: list[Finding],
) -> None:
    num_courses = inputs.get("numCourses")
    prerequisites = inputs.get("prerequisites")
    if type(num_courses) is not int or num_courses < 0:
        findings.append(error(path, f"case {index} input.numCourses must be a non-negative integer"))
        return
    if not isinstance(prerequisites, list):
        findings.append(error(path, f"case {index} input.prerequisites must be a list of two-integer edges"))
        return
    for edge_index, edge in enumerate(prerequisites, start=1):
        if (
            not isinstance(edge, list)
            or len(edge) != 2
            or type(edge[0]) is not int
            or type(edge[1]) is not int
        ):
            findings.append(error(path, f"case {index} input.prerequisites[{edge_index}] must be a two-integer edge"))
            continue
        if edge[0] < 0 or edge[0] >= num_courses or edge[1] < 0 or edge[1] >= num_courses:
            findings.append(error(path, f"case {index} input.prerequisites[{edge_index}] contains an out-of-range course"))


def text_reuses_blocked_source_example(text: str) -> bool:
    hashes = blocked_source_example_hashes()
    if not hashes:
        return False
    return any(blocked_source_example_hash(candidate) in hashes for candidate in text_fingerprint_candidates(text))


def source_example_fingerprint_is_blocked(value: Any) -> bool:
    hashes = blocked_source_example_hashes()
    return bool(hashes) and blocked_source_example_hash(value) in hashes


def blocked_source_example_hash(value: Any) -> str:
    return sha256(case_fingerprint(value).encode("utf-8")).hexdigest()


def blocked_source_example_hashes() -> set[str]:
    hashes: set[str] = set()
    inline_hashes = os.environ.get(BLOCKED_SOURCE_HASHES_ENV, "")
    for token in re.split(r"[\s,]+", inline_hashes.strip()):
        if SHA256_HEX_PATTERN.fullmatch(token):
            hashes.add(token)

    hash_file = os.environ.get(BLOCKED_SOURCE_HASH_FILE_ENV)
    if hash_file:
        try:
            for line in Path(hash_file).read_text(encoding="utf-8").splitlines():
                token = line.strip()
                if not token or token.startswith("#"):
                    continue
                if SHA256_HEX_PATTERN.fullmatch(token):
                    hashes.add(token)
        except OSError:
            pass
    return hashes


def validate_blocked_source_hash_file_config(findings: list[Finding]) -> None:
    hash_file = os.environ.get(BLOCKED_SOURCE_HASH_FILE_ENV)
    if not hash_file:
        return
    try:
        Path(hash_file).read_text(encoding="utf-8")
    except OSError as exc:
        detail = exc.strerror or str(exc)
        findings.append(error(Path(hash_file), f"{BLOCKED_SOURCE_HASH_FILE_ENV} is set but cannot be read: {detail}"))


def text_fingerprint_candidates(text: str) -> list[str]:
    candidates = [text]
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        candidates.append(stripped)
        if "|" in stripped:
            candidates.extend(clean_markdown_candidate(cell) for cell in stripped.split("|") if clean_markdown_candidate(cell))
    candidates.extend(clean_markdown_candidate(candidate) for candidate in list(candidates) if clean_markdown_candidate(candidate))
    return candidates


def clean_markdown_candidate(value: str) -> str:
    return value.strip().strip("`").strip()


def validate_expected_mutations(
    path: Path,
    index: int,
    expected_mutations: Any,
    parameter_names: list[str],
    java_parameter_types: dict[str, Any],
    python_parameter_types: dict[str, Any],
    findings: list[Finding],
    custom_node_kind: Any = None,
) -> None:
    if not isinstance(expected_mutations, dict) or not expected_mutations:
        findings.append(error(path, f"case {index} expectedMutations must be a non-empty object"))
        return

    for parameter_name, expectation in expected_mutations.items():
        valid_target = True
        if not isinstance(parameter_name, str) or parameter_name not in parameter_names:
            findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must name a signature parameter"))
            valid_target = False
        java_type = java_parameter_types.get(parameter_name)
        python_type = python_parameter_types.get(parameter_name)
        if valid_target and (
            java_type not in SUPPORTED_JAVA_MUTATION_TYPES or python_type not in SUPPORTED_PYTHON_MUTATION_TYPES
        ):
            findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must target a mutable generated-driver parameter"))

        if isinstance(expectation, dict) and ("prefix" in expectation or "lengthFrom" in expectation):
            if java_type == "TreeNode" and python_type == "Optional[TreeNode]":
                findings.append(error(path, f"case {index} expectedMutations.{parameter_name} prefix mutations are not supported for TreeNode"))
            if java_type == "Node" and python_type == "Optional[Node]":
                findings.append(error(path, f"case {index} expectedMutations.{parameter_name} prefix mutations are not supported for Node"))
            allowed_keys = {"prefix", "lengthFrom"}
            unexpected = sorted(set(expectation) - allowed_keys)
            for key in unexpected:
                findings.append(error(path, f"case {index} expectedMutations.{parameter_name}.{key} is not supported"))
            if "prefix" not in expectation:
                findings.append(error(path, f"case {index} expectedMutations.{parameter_name} prefix is required"))
            if expectation.get("lengthFrom") != "return":
                findings.append(error(path, f"case {index} expectedMutations.{parameter_name} lengthFrom must be return"))
        elif valid_target and java_type == "TreeNode" and python_type == "Optional[TreeNode]" and not is_tree_node_value(expectation):
            findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must match TreeNode/Optional[TreeNode]"))
        elif valid_target and java_type == "Node" and python_type == "Optional[Node]":
            if custom_node_kind == "binary-tree-next" and not is_list_of_int_lists(expectation):
                findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must match Node/Optional[Node] next-level values"))
            elif custom_node_kind == "graph" and not is_graph_adjacency_value(expectation):
                findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must match Node/Optional[Node] graph adjacency values"))
            elif custom_node_kind == "quad-tree" and not is_quad_tree_value(expectation):
                findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must match Node/Optional[Node] quad-tree values"))
            elif custom_node_kind == "random-list" and not is_random_list_value(expectation):
                findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must match Node/Optional[Node] random-list values"))
            elif custom_node_kind not in SUPPORTED_CUSTOM_NODE_TYPES:
                findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must define a supported signature.customTypes.Node"))
        elif valid_target and java_type == "ListNode" and python_type == "Optional[ListNode]" and not is_linked_list_input(expectation):
            findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must match ListNode/Optional[ListNode]"))
        elif valid_target and java_type == "int[]" and python_type == "List[int]" and not is_list_of_ints(expectation):
            findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must match int[]/List[int]"))
        elif valid_target and java_type == "int[][]" and python_type == "List[List[int]]" and not is_list_of_int_lists(expectation):
            findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must match int[][]/List[List[int]]"))
        elif valid_target and java_type == "char[]" and python_type == "List[str]" and not is_list_of_chars(expectation):
            findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must match char[]/List[str]"))
        elif valid_target and java_type == "char[][]" and python_type == "List[List[str]]" and not is_char_grid(expectation):
            findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must match char[][]/List[List[str]]"))
        elif valid_target and java_type == "String[]" and python_type == "List[str]" and not is_list_of_strings(expectation):
            findings.append(error(path, f"case {index} expectedMutations.{parameter_name} must match String[]/List[str]"))


def validate_linked_list_contract(
    path: Path,
    index: int,
    contract: Any,
    inputs: dict[str, Any],
    parameter_names: list[str],
    java_parameter_types: dict[str, Any],
    python_parameter_types: dict[str, Any],
    java_return_type: Any,
    python_return_type: Any,
    findings: list[Finding],
) -> None:
    if not isinstance(contract, dict) or not contract:
        findings.append(error(path, f"case {index} linkedListContract must be a non-empty object"))
        return

    validate_allowed_keys(path, contract, ALLOWED_LINKED_LIST_CONTRACT_KEYS, f"case {index} linkedListContract", findings)

    result = contract.get("result")
    if result is not None:
        if not isinstance(result, dict):
            findings.append(error(path, f"case {index} linkedListContract.result must be an object"))
        else:
            validate_allowed_keys(
                path,
                result,
                ALLOWED_LINKED_LIST_RESULT_KEYS,
                f"case {index} linkedListContract.result",
                findings,
            )
            source_name = result.get("from")
            if not require_text(source_name):
                findings.append(error(path, f"case {index} linkedListContract.result.from is required"))
            elif source_name not in parameter_names:
                findings.append(error(path, f"case {index} linkedListContract.result.from must name a signature parameter"))
            elif not is_list_node_parameter(source_name, java_parameter_types, python_parameter_types):
                findings.append(error(path, f"case {index} linkedListContract.result.from must target a ListNode parameter"))
            if java_return_type != "ListNode" or python_return_type != "Optional[ListNode]":
                findings.append(error(path, f"case {index} linkedListContract.result requires a ListNode return signature"))
            validate_node_indices(
                path,
                index,
                "linkedListContract.result.nodeIndices",
                result.get("nodeIndices"),
                inputs.get(source_name) if isinstance(source_name, str) else None,
                findings,
            )

    post_call = contract.get("postCall")
    if post_call is not None:
        if not isinstance(post_call, dict) or not post_call:
            findings.append(error(path, f"case {index} linkedListContract.postCall must be a non-empty object"))
        else:
            for parameter_name, node_indices in post_call.items():
                if not isinstance(parameter_name, str) or parameter_name not in parameter_names:
                    findings.append(error(path, f"case {index} linkedListContract.postCall.{parameter_name} must name a signature parameter"))
                    continue
                if not is_list_node_parameter(parameter_name, java_parameter_types, python_parameter_types):
                    findings.append(error(path, f"case {index} linkedListContract.postCall.{parameter_name} must target a ListNode parameter"))
                    continue
                validate_node_indices(
                    path,
                    index,
                    f"linkedListContract.postCall.{parameter_name}",
                    node_indices,
                    inputs.get(parameter_name),
                    findings,
                )


def is_list_node_parameter(
    parameter_name: str,
    java_parameter_types: dict[str, Any],
    python_parameter_types: dict[str, Any],
) -> bool:
    return (
        java_parameter_types.get(parameter_name) == "ListNode"
        and python_parameter_types.get(parameter_name) == "Optional[ListNode]"
    )


def validate_node_indices(
    path: Path,
    index: int,
    label: str,
    node_indices: Any,
    input_value: Any,
    findings: list[Finding],
) -> None:
    if not isinstance(node_indices, list) or not all(type(item) is int and item >= 0 for item in node_indices):
        findings.append(error(path, f"case {index} {label} must be a list of non-negative integer indices"))
        return
    if input_value is None:
        if node_indices:
            findings.append(error(path, f"case {index} {label} must be empty for null input"))
        return
    if is_cyclic_linked_list_input(input_value):
        findings.append(error(path, f"case {index} {label} cannot reference cyclic ListNode input"))
        return
    input_length = linked_list_input_length(input_value)
    if input_length is None:
        findings.append(error(path, f"case {index} {label} must reference a list-valued ListNode input"))
        return
    if any(item >= input_length for item in node_indices):
        findings.append(error(path, f"case {index} {label} contains an out-of-range node index"))


def case_fingerprint(case: dict[str, Any]) -> str:
    def normalize(value: Any) -> str:
        if isinstance(value, str):
            return "".join(char.lower() for char in value if char.isalnum())
        if isinstance(value, list):
            return "[" + ",".join(normalize(item) for item in value) + "]"
        if isinstance(value, dict):
            return "|".join(f"{str(key).lower()}:{normalize(value[key])}" for key in sorted(value))
        return str(value).lower()

    return normalize(case)


def validate_solution_tiers(
    problem_dir: Path,
    solutions_path: Path,
    solutions: list[Any],
    findings: list[Finding],
    completed: bool,
) -> None:
    tiers: list[int] = []
    for solution in solutions:
        if not isinstance(solution, dict):
            findings.append(error(solutions_path, "solution entry must be an object"))
            continue
        tier = solution.get("tier")
        if isinstance(tier, int):
            tiers.append(tier)
        else:
            findings.append(error(solutions_path, "solution tier must be an integer"))

        for key in ("timeComplexity", "spaceComplexity"):
            complexity = solution.get(key)
            if not isinstance(complexity, dict):
                findings.append(error(solutions_path, f"{key} is required"))
                continue
            if not require_text(complexity.get("class")):
                findings.append(error(solutions_path, f"{key}.class is required"))
            if not require_text(complexity.get("explanation")):
                findings.append(error(solutions_path, f"{key}.explanation is required"))

        for path_key in ("javaPath", "pythonPath"):
            value = solution.get(path_key)
            if not require_text(value):
                findings.append(error(solutions_path, f"missing {path_key}"))
                continue
            language = "java" if path_key == "javaPath" else "python"
            if path_contains_symlink(problem_dir / value, problem_dir):
                findings.append(error(problem_dir / value, f"{path_key} must not be a symlink"))
                continue
            resolved, message = resolve_solution_path(problem_dir, value, language)
            if message is not None:
                findings.append(error(solutions_path, f"{path_key} {message}"))
                continue
            if completed and resolved is not None and not resolved.is_file():
                findings.append(error(resolved, f"{path_key} does not exist"))
            if completed and path_key == "pythonPath" and resolved is not None and resolved.is_file():
                text = resolved.read_text(encoding="utf-8")
                if python_source_uses_builtin_generics_without_future(text):
                    findings.append(
                        error(
                            resolved,
                            "pythonPath uses Python 3.9 built-in generics without postponed annotations",
                        )
                    )

    if tiers and sorted(tiers) != list(range(1, len(tiers) + 1)):
        findings.append(error(solutions_path, "solution tiers must be contiguous starting at 1"))


def resolve_solution_path(problem_dir: Path, value: str, language: str) -> tuple[Path | None, str | None]:
    if not require_text(value):
        return None, "is required"

    candidate = Path(value)
    if candidate.is_absolute():
        return None, "must be relative"

    parts = candidate.parts
    if not parts or parts[0] != language:
        return None, f"must live under {language}/"

    problem_root = problem_dir.resolve()
    language_root = (problem_dir / language).resolve()
    resolved = (problem_dir / candidate).resolve()
    try:
        resolved.relative_to(problem_root)
        resolved.relative_to(language_root)
    except ValueError:
        return None, "must not escape the problem language directory"

    return resolved, None


def load_source_index(root: Path) -> dict[str, dict[str, dict[str, Any]]]:
    source_dir = root / "resources" / "source-intake" / "coding-lists"
    index: dict[str, dict[str, dict[str, Any]]] = {}
    if not source_dir.is_dir():
        return index
    for path in sorted(source_dir.glob("*.json")):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        collection_id = payload.get("collectionId")
        if not require_text(collection_id):
            continue
        collection_items = index.setdefault(collection_id, {})
        for item in payload.get("items", []):
            if isinstance(item, dict) and require_text(item.get("canonicalId")):
                collection_items[item["canonicalId"]] = item
    return index


def validate_problem_collection_membership(
    path: Path,
    problem_id: str,
    collection: dict[str, Any],
    source_index: dict[str, dict[str, dict[str, Any]]],
    findings: list[Finding],
) -> None:
    collection_id = collection.get("id")
    if not source_index:
        return
    if collection_id not in source_index:
        findings.append(error(path, f"collection {collection_id} source manifest is missing"))
        return
    source_item = source_index.get(collection_id, {}).get(problem_id)
    if source_item is None:
        findings.append(error(path, f"collection {collection_id} does not contain {problem_id} in source manifests"))
        return
    for field in ("order", "group", "sourceUrl"):
        if collection.get(field) != source_item.get(field):
            findings.append(error(path, f"collection {collection_id} {field} must match source manifest"))


def validate_problem_collection_membership_set(
    path: Path,
    problem_id: str,
    collections: list[Any],
    source_index: dict[str, dict[str, dict[str, Any]]],
    findings: list[Finding],
) -> None:
    if not source_index:
        return
    expected = {
        collection_id
        for collection_id, items in source_index.items()
        if problem_id in items
    }
    declared = {
        collection.get("id")
        for collection in collections
        if isinstance(collection, dict) and require_text(collection.get("id"))
    }
    for collection_id in sorted(expected - declared):
        findings.append(error(path, f"missing collection membership {collection_id} from source manifests"))


def validate_url(
    path: Path,
    value: Any,
    allowed_hosts: set[str],
    label: str,
    findings: list[Finding],
) -> None:
    if not require_text(value):
        findings.append(error(path, f"{label} is required"))
        return
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.netloc not in allowed_hosts:
        findings.append(error(path, f"{label} must use https and an allowed host"))


def validate_source_manifests(
    manifests: list[dict[str, Any]],
    strict: bool = True,
    collection: str | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    for manifest in manifests:
        path = Path(manifest["path"])
        payload = manifest["payload"]
        load_error = manifest.get("error")
        if load_error:
            findings.append(error(path, f"source manifest JSON is invalid: {load_error}"))
            continue
        if collection and source_manifest_collection_id(path, payload) != collection:
            continue
        if not isinstance(payload, dict):
            findings.append(error(path, "source manifest must be an object"))
            continue

        validate_allowed_keys(path, payload, ALLOWED_SOURCE_TOP_LEVEL_KEYS, "source manifest", findings)
        collection_id = payload.get("collectionId")
        if not require_text(collection_id):
            findings.append(error(path, "collectionId is required"))
        elif not COLLECTION_ID_PATTERN.fullmatch(collection_id):
            findings.append(error(path, f"collectionId {collection_id} is not a safe slug"))
        validate_url(path, payload.get("sourceUrl"), SOURCE_URL_HOSTS, "sourceUrl", findings)
        validate_source_route(path, collection_id, payload.get("sourceUrl"), findings)
        source_status = payload.get("sourceStatus")
        if source_status not in VALID_SOURCE_STATUSES:
            findings.append(error(path, f"sourceStatus must be one of {sorted(VALID_SOURCE_STATUSES)}"))
            continue

        items = payload.get("items")
        if not isinstance(items, list):
            findings.append(error(path, "items must be a list"))
            continue

        if source_status == "blocked-source-unpinned":
            message = "source snapshot is not pinned"
            findings.append(error(path, message) if strict else warning(path, message))
            continue

        snapshot_date = payload.get("snapshotDate")
        if not is_iso_date(snapshot_date):
            findings.append(error(path, "snapshotDate must be an ISO date"))
        validate_source_provenance(path, payload, findings)

        expected_count = payload.get("expectedCount")
        if not isinstance(expected_count, int):
            findings.append(error(path, "expectedCount must be an integer for pinned source manifests"))
        elif expected_count != len(items):
            findings.append(
                error(path, f"expectedCount {expected_count} does not match item count {len(items)}")
            )

        seen_orders: set[int] = set()
        seen_source_ids: set[str] = set()
        seen_canonical_ids: set[str] = set()
        seen_dedupe_keys: set[str] = set()

        for index, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                findings.append(error(path, f"item {index} must be an object"))
                continue
            validate_allowed_keys(path, item, ALLOWED_SOURCE_ITEM_KEYS, f"item {index}", findings)
            for field in REQUIRED_SOURCE_ITEM_KEYS:
                value = item.get(field)
                if field == "order":
                    if not isinstance(value, int):
                        findings.append(error(path, f"item {index} missing integer order"))
                    else:
                        if value in seen_orders:
                            findings.append(error(path, f"duplicate order {value}"))
                        seen_orders.add(value)
                elif not require_text(value):
                    findings.append(error(path, f"item {index} missing {field}"))
            track_unique_source_item_fields(
                path,
                index,
                item,
                seen_source_ids,
                seen_canonical_ids,
                seen_dedupe_keys,
                findings,
            )
            validate_url(path, item.get("sourceUrl"), PROBLEM_URL_HOSTS, f"item {index} sourceUrl", findings)
            if "paidOnly" in item and not isinstance(item.get("paidOnly"), bool):
                findings.append(error(path, f"item {index} paidOnly must be boolean when present"))
            if item.get("collectionId") != collection_id:
                findings.append(error(path, f"item {index} collectionId does not match manifest"))
            validate_source_item_metadata(path, item, index, findings)
            validate_leetcode_item_consistency(path, item, index, findings)

        if seen_orders and sorted(seen_orders) != list(range(1, len(items) + 1)):
            findings.append(error(path, "orders must be contiguous starting at 1"))

    return findings


def source_manifest_collection_id(path: Path, payload: Any) -> str | None:
    if isinstance(payload, dict):
        collection_id = payload.get("collectionId")
        return collection_id if isinstance(collection_id, str) else None
    return path.stem


def track_unique_source_item_fields(
    path: Path,
    index: int,
    item: dict[str, Any],
    seen_source_ids: set[str],
    seen_canonical_ids: set[str],
    seen_dedupe_keys: set[str],
    findings: list[Finding],
) -> None:
    for field, seen_values in (
        ("sourceId", seen_source_ids),
        ("canonicalId", seen_canonical_ids),
        ("dedupeKey", seen_dedupe_keys),
    ):
        value = item.get(field)
        if not require_text(value):
            continue
        if value in seen_values:
            findings.append(error(path, f"item {index} duplicate {field} {value}"))
        seen_values.add(value)


def validate_allowed_keys(
    path: Path,
    payload: dict[str, Any],
    allowed_keys: set[str],
    label: str,
    findings: list[Finding],
) -> None:
    for key in sorted(payload.keys() - allowed_keys):
        if key in BLOCKED_SOURCE_TEXT_KEYS:
            findings.append(error(path, f"{label} contains forbidden source-derived field {key}"))
        else:
            findings.append(error(path, f"{label} contains unsupported field {key}"))


def validate_no_source_derived_keys(
    path: Path,
    payload: Any,
    label: str,
    findings: list[Finding],
) -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            next_label = f"{label}.{key}"
            if key.lower() in BLOCKED_SOURCE_TEXT_KEYS and not is_allowed_solution_metadata_key(label, key):
                findings.append(error(path, f"{next_label} contains forbidden source-derived field {key}"))
            validate_no_source_derived_keys(path, value, next_label, findings)
    elif isinstance(payload, list):
        for index, value in enumerate(payload, start=1):
            validate_no_source_derived_keys(path, value, f"{label}[{index}]", findings)
    elif isinstance(payload, str) and source_example_fingerprint_is_blocked(payload):
        findings.append(error(path, "content appears to reuse a blocked source example"))


def is_allowed_solution_metadata_key(label: str, key: str) -> bool:
    return key == "explanation" and label.rsplit(".", 1)[-1] in {"timeComplexity", "spaceComplexity"}


def validate_leetcode_item_consistency(
    path: Path,
    item: dict[str, Any],
    index: int,
    findings: list[Finding],
) -> None:
    source_id = item.get("sourceId")
    title_slug = item.get("titleSlug")
    source_url = item.get("sourceUrl")
    canonical_id = item.get("canonicalId")
    dedupe_key = item.get("dedupeKey")

    if not require_text(title_slug) or not require_text(source_id):
        return

    expected_url = f"https://leetcode.com/problems/{title_slug}"
    if source_url != expected_url:
        findings.append(error(path, f"item {index} sourceUrl must be {expected_url}"))

    if source_id.isdigit():
        expected_canonical_id = f"lc-{int(source_id):04d}-{title_slug}"
        if canonical_id != expected_canonical_id:
            findings.append(error(path, f"item {index} canonicalId must be {expected_canonical_id}"))
        expected_dedupe_keys = {
            f"leetcode:{source_id}:{title_slug}",
            f"leetcode-slug:{title_slug}",
        }
        if dedupe_key not in expected_dedupe_keys:
            findings.append(error(path, f"item {index} dedupeKey must reference sourceId and titleSlug"))


def validate_source_item_metadata(
    path: Path,
    item: dict[str, Any],
    index: int,
    findings: list[Finding],
) -> None:
    source_id = item.get("sourceId")
    title_slug = item.get("titleSlug")
    difficulty = item.get("difficulty")

    if require_text(source_id) and not source_id.isdigit():
        findings.append(error(path, f"item {index} sourceId must be numeric LeetCode metadata"))
    if require_text(title_slug) and not TITLE_SLUG_PATTERN.fullmatch(title_slug):
        findings.append(error(path, f"item {index} titleSlug must be a lowercase URL slug"))
    if difficulty not in SOURCE_DIFFICULTIES:
        findings.append(error(path, f"item {index} difficulty must be one of {sorted(SOURCE_DIFFICULTIES)}"))
    validate_plain_source_metadata_text(path, item.get("title"), index, "title", 120, findings)
    validate_plain_source_metadata_text(path, item.get("group"), index, "group", 80, findings)


def validate_plain_source_metadata_text(
    path: Path,
    value: Any,
    index: int,
    field: str,
    max_length: int,
    findings: list[Finding],
) -> None:
    if not require_text(value):
        return
    if len(value) > max_length:
        findings.append(error(path, f"item {index} {field} must be at most {max_length} characters"))
    if not PLAIN_METADATA_TEXT_PATTERN.fullmatch(value):
        findings.append(error(path, f"item {index} {field} must be plain metadata text"))


def validate_source_route(path: Path, collection_id: Any, source_url: Any, findings: list[Finding]) -> None:
    if not isinstance(collection_id, str):
        return
    expected = SOURCE_ROUTE_ALLOWLIST.get(collection_id)
    if expected is None or not isinstance(source_url, str):
        return
    if source_url != expected:
        findings.append(error(path, f"sourceUrl for {collection_id} must be {expected}"))


def validate_source_provenance(path: Path, payload: dict[str, Any], findings: list[Finding]) -> None:
    provenance = payload.get("provenance")
    if not isinstance(provenance, dict):
        findings.append(error(path, "pinned source manifest must define provenance"))
        return
    validate_allowed_keys(path, provenance, REQUIRED_SOURCE_PROVENANCE_KEYS, "source provenance", findings)
    for key in REQUIRED_SOURCE_PROVENANCE_KEYS:
        if key == "sourcePages":
            pages = provenance.get(key)
            if not isinstance(pages, list) or not pages or not all(require_text(page) for page in pages):
                findings.append(error(path, "provenance.sourcePages must be a non-empty list of URLs"))
            else:
                for index, page in enumerate(pages, start=1):
                    validate_url(path, page, SOURCE_URL_HOSTS, f"provenance.sourcePages[{index}]", findings)
            continue
        if key in {"fetchDate"}:
            if not is_iso_date(provenance.get(key)):
                findings.append(error(path, f"provenance.{key} must be an ISO date"))
            continue
        if not require_text(provenance.get(key)):
            findings.append(error(path, f"provenance.{key} is required"))

    expected_hash = source_metadata_hash(payload.get("items", []))
    if provenance.get("metadataSha256") != expected_hash:
        findings.append(error(path, "provenance.metadataSha256 must match the normalized items payload"))


def source_metadata_hash(items: Any) -> str:
    normalized = json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(normalized.encode("utf-8")).hexdigest()


def is_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True
