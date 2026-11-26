"""Generated driver execution for coding problem solutions."""

from __future__ import annotations

import copy
import json
import math
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import textwrap
import uuid
from pathlib import Path
from typing import Any

from .load import load_catalog
from .schema import (
    COMPLETED_STATUSES,
    SUPPORTED_JAVA_PARAMETER_TYPES,
    SUPPORTED_JAVA_RETURN_TYPES,
    Finding,
    error,
    is_safe_identifier,
    resolve_solution_path,
)


DRIVER_TIMEOUT_SECONDS = 10
MIN_JAVA_MAJOR_VERSION = 11
JAVA_VERSION_PATTERN = re.compile(r'(?:version\s+)?"(?P<quoted>[0-9][^"]*)"|(?P<plain>[0-9]+(?:\.[0-9]+)*)')


def validate_driver_generation(root: Path, problem_id: str | None = None) -> tuple[list[Finding], int]:
    catalog = load_catalog(root)
    findings: list[Finding] = []
    count = 0
    for record in catalog:
        problem = record.get("problem")
        if not isinstance(problem, dict):
            continue
        if problem_id is not None and problem.get("id") != problem_id:
            continue
        if problem.get("status") not in COMPLETED_STATUSES:
            continue
        count += 1
        problem_dir = Path(record["dir"])
        cases = record.get("cases")
        signature = problem.get("signature")
        if not isinstance(signature, dict) or not isinstance(signature.get("java"), dict):
            findings.append(error(problem_dir / "problem.json", "driver generation requires Java signature"))
            continue
        if not isinstance(cases, dict) or not cases.get("cases"):
            findings.append(error(problem_dir / "cases.json", "driver generation requires at least one test case"))
            continue
        java_signature = java_language_signature(signature)
        signature_findings = validate_java_driver_signature(java_signature, problem_dir / "problem.json")
        if signature_findings:
            findings.extend(signature_findings)
            continue
        try:
            java_driver_source(java_signature, cases)
        except Exception as exc:
            findings.append(error(problem_dir / "cases.json", f"Java driver generation failed: {exc}"))
    if problem_id is not None and count == 0:
        findings.append(error(root / "05-coding-problems" / "problem-bank", f"problem {problem_id} not found for driver generation"))
    return findings, count


def run_problem_drivers(
    root: Path,
    problem_id: str,
    language: str,
    *,
    allow_unsafe_driver_execution: bool = False,
) -> list[Finding]:
    if not allow_unsafe_driver_execution:
        return [
            error(
                root / "05-coding-problems" / "problem-bank",
                "driver execution requires allow_unsafe_driver_execution=True",
            )
        ]
    catalog = load_catalog(root)
    record = next(
        (
            item
            for item in catalog
            if isinstance(item.get("problem"), dict) and item["problem"].get("id") == problem_id
        ),
        None,
    )
    if record is None:
        return [error(root / "05-coding-problems" / "problem-bank", f"problem {problem_id} not found")]

    if language == "python":
        return run_python_drivers(record)
    if language == "java":
        return run_java_drivers(record)
    return [error(record["dir"], f"unsupported driver language {language}")]


def run_python_drivers(record: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    problem_dir = Path(record["dir"])
    problem = record["problem"]
    cases = record["cases"] or {}
    solutions = (record["solutions"] or {}).get("solutions", [])
    problem_signature = problem["signature"]
    signature = problem_signature["python"]
    class_name = signature["className"]
    parameters = signature.get("parameters", [])
    kind = problem_signature.get("kind", "function")
    if not cases.get("cases"):
        return [error(problem_dir / "cases.json", "driver requires at least one test case")]

    for solution in solutions:
        path, message = resolve_solution_path(problem_dir, solution.get("pythonPath", ""), "python")
        if message is not None or path is None:
            findings.append(error(problem_dir / "solutions.json", f"pythonPath {message}"))
            continue
        findings.extend(
            run_python_solution_subprocess(
                path,
                python_driver_payload(kind, class_name, signature, parameters, problem_signature.get("customTypes", {}), cases),
            )
        )

    return findings


def python_driver_payload(
    kind: str,
    class_name: str,
    signature: dict[str, Any],
    parameters: list[dict[str, Any]],
    custom_types: dict[str, Any],
    cases: dict[str, Any],
) -> dict[str, Any]:
    if kind == "object":
        return {
            "kind": "object",
            "className": class_name,
            "constructor": signature.get("constructor"),
            "methods": signature.get("methods"),
            "customTypes": custom_types,
            "cases": cases,
        }
    return {
        "kind": "function",
        "className": class_name,
        "methodName": signature["methodName"],
        "returnType": signature["returnType"],
        "parameters": parameters,
        "customTypes": custom_types,
        "cases": cases,
    }


def java_language_signature(signature: dict[str, Any]) -> dict[str, Any]:
    java_signature = dict(signature["java"])
    if signature.get("kind") == "object":
        java_signature["kind"] = "object"
    if "customTypes" in signature:
        java_signature["customTypes"] = signature["customTypes"]
    return java_signature


def run_python_solution_subprocess(solution_path: Path, payload: dict[str, Any]) -> list[Finding]:
    runner_source = textwrap.dedent(
        """
        import copy
        import importlib.util
        import json
        import math
        import sys
        import uuid
        from pathlib import Path
        from typing import List, Optional


        class ListNode:
            def __init__(self, val=0, next=None):
                self.val = val
                self.next = next


        class TreeNode:
            def __init__(self, val=0, left=None, right=None):
                self.val = val
                self.left = left
                self.right = right


        class BinaryTreeNextNode:
            def __init__(self, val=0, left=None, right=None, next=None):
                self.val = val
                self.left = left
                self.right = right
                self.next = next


        class RandomListNode:
            def __init__(self, x=0, next=None, random=None):
                self.val = x
                self.next = next
                self.random = random


        class GraphNode:
            def __init__(self, val=0, neighbors=None):
                self.val = val
                self.neighbors = [] if neighbors is None else neighbors


        class QuadTreeNode:
            def __init__(self, val=False, isLeaf=False, topLeft=None, topRight=None, bottomLeft=None, bottomRight=None):
                self.val = val
                self.isLeaf = isLeaf
                self.topLeft = topLeft
                self.topRight = topRight
                self.bottomLeft = bottomLeft
                self.bottomRight = bottomRight


        Node = BinaryTreeNextNode


        def node_class_for_custom_types(custom_types):
            if isinstance(custom_types, dict) and custom_types.get("Node") == "random-list":
                return RandomListNode
            if isinstance(custom_types, dict) and custom_types.get("Node") == "graph":
                return GraphNode
            if isinstance(custom_types, dict) and custom_types.get("Node") == "quad-tree":
                return QuadTreeNode
            return BinaryTreeNextNode


        def matches(matcher, actual, expected, case, matcher_config=None):
            if matcher == "exact":
                return actual == expected
            if matcher == "unordered-list":
                return canonical_flat_list(actual) == canonical_flat_list(expected)
            if matcher == "unordered-list-of-lists":
                return canonical_nested_list(actual) == canonical_nested_list(expected)
            if matcher == "unordered-tree-list":
                return canonical_tree_list(actual) == canonical_tree_list(expected)
            if matcher == "float-tolerance":
                return float_tolerance_matches(
                    actual,
                    expected,
                    matcher_config.get("tolerance") if isinstance(matcher_config, dict) else None,
                )
            if matcher == "valid-topological-order":
                return valid_topological_order(
                    actual,
                    case["input"].get("numCourses"),
                    case["input"].get("prerequisites"),
                )
            if matcher == "two-sum-indices":
                if not isinstance(actual, list) or len(actual) != 2:
                    return False
                nums = case["input"]["nums"]
                target = case["input"]["target"]
                i, j = actual
                return (
                    isinstance(i, int)
                    and isinstance(j, int)
                    and i != j
                    and 0 <= i < len(nums)
                    and 0 <= j < len(nums)
                    and nums[i] + nums[j] == target
                )
            if matcher == "balanced-bst-from-sorted-array":
                return tree_matches_sorted_array(actual, case["input"].get("nums"))
            return actual == expected


        def object_matches(matcher, actual, expected, operation, matcher_config=None):
            if matcher == "object-one-of":
                if isinstance(expected, dict) and set(expected) == {"oneOf"} and isinstance(expected.get("oneOf"), list):
                    return actual in expected["oneOf"]
                return actual == expected
            return matches(matcher, actual, expected, operation, matcher_config)


        def canonical_flat_list(value):
            if not isinstance(value, list):
                return None
            return sorted(json.dumps(item, separators=(",", ":")) for item in value)


        def canonical_nested_list(value):
            if not isinstance(value, list):
                return None
            rows = []
            for row in value:
                if not isinstance(row, list):
                    return None
                rows.append(json.dumps(row, separators=(",", ":")))
            return sorted(rows)


        def canonical_tree_list(value):
            if not isinstance(value, list):
                return None
            rows = []
            for tree in value:
                if isinstance(tree, TreeNode) or tree is None:
                    rows.append(json.dumps(tree_values(tree), separators=(",", ":")))
                elif isinstance(tree, list):
                    rows.append(json.dumps(tree, separators=(",", ":")))
                else:
                    return None
            return sorted(rows)


        def is_finite_number(value):
            return type(value) in (int, float) and math.isfinite(float(value))


        def float_tolerance_matches(actual, expected, tolerance):
            if not is_finite_number(tolerance) or tolerance <= 0:
                return False
            if is_finite_number(expected):
                return is_finite_number(actual) and abs(float(actual) - float(expected)) <= tolerance
            if isinstance(expected, list):
                if not isinstance(actual, list) or len(actual) != len(expected):
                    return False
                return all(float_tolerance_matches(left, right, tolerance) for left, right in zip(actual, expected))
            return False


        def valid_topological_order(actual, num_courses, prerequisites):
            if not valid_topological_input(num_courses, prerequisites):
                return False
            if not isinstance(actual, list) or not all(type(item) is int for item in actual):
                return False
            if len(actual) == 0:
                return num_courses == 0 or not has_topological_order(num_courses, prerequisites)
            if len(actual) != num_courses:
                return False
            position = [-1] * num_courses
            for index, course in enumerate(actual):
                if course < 0 or course >= num_courses or position[course] != -1:
                    return False
                position[course] = index
            for edge in prerequisites:
                if (
                    not isinstance(edge, list)
                    or len(edge) != 2
                    or type(edge[0]) is not int
                    or type(edge[1]) is not int
                    or edge[0] < 0
                    or edge[0] >= num_courses
                    or edge[1] < 0
                    or edge[1] >= num_courses
                    or position[edge[1]] >= position[edge[0]]
                ):
                    return False
            return True


        def valid_topological_input(num_courses, prerequisites):
            if type(num_courses) is not int or num_courses < 0:
                return False
            if not isinstance(prerequisites, list):
                return False
            for edge in prerequisites:
                if (
                    not isinstance(edge, list)
                    or len(edge) != 2
                    or type(edge[0]) is not int
                    or type(edge[1]) is not int
                    or edge[0] < 0
                    or edge[0] >= num_courses
                    or edge[1] < 0
                    or edge[1] >= num_courses
                ):
                    return False
            return True


        def has_topological_order(num_courses, prerequisites):
            graph = [[] for _ in range(num_courses)]
            indegree = [0] * num_courses
            for edge in prerequisites:
                graph[edge[1]].append(edge[0])
                indegree[edge[0]] += 1
            queue = [course for course in range(num_courses) if indegree[course] == 0]
            seen = 0
            index = 0
            while index < len(queue):
                course = queue[index]
                index += 1
                seen += 1
                for nxt in graph[course]:
                    indegree[nxt] -= 1
                    if indegree[nxt] == 0:
                        queue.append(nxt)
            return seen == num_courses


        def tree_matches_sorted_array(values, nums):
            if not isinstance(nums, list) or not all(type(item) is int for item in nums):
                return False
            if values == []:
                return nums == []
            try:
                root = build_tree(values)
            except Exception:
                return False
            inorder_values = []

            def collect_inorder(node):
                if node is None:
                    return
                collect_inorder(node.left)
                inorder_values.append(node.val)
                collect_inorder(node.right)

            def balanced_height(node):
                if node is None:
                    return 0
                left_height = balanced_height(node.left)
                if left_height < 0:
                    return -1
                right_height = balanced_height(node.right)
                if right_height < 0:
                    return -1
                if abs(left_height - right_height) > 1:
                    return -1
                return max(left_height, right_height) + 1

            collect_inorder(root)
            return inorder_values == nums and balanced_height(root) >= 0


        def mutation_actual_value(expectation, actual_return, value, parameter_type=None, custom_types=None):
            if isinstance(expectation, dict) and ("prefix" in expectation or "lengthFrom" in expectation):
                if expectation.get("lengthFrom") != "return":
                    raise ValueError("unsupported mutation length source")
                if not isinstance(actual_return, int):
                    raise ValueError("prefix mutation assertion requires an integer return value")
                return value[:actual_return], expectation.get("prefix")
            if parameter_type == "Optional[ListNode]":
                return list_node_values(value), expectation
            if isinstance(value, Node):
                if isinstance(custom_types, dict) and custom_types.get("Node") == "graph":
                    return graph_adjacency_values(value), expectation
                if isinstance(custom_types, dict) and custom_types.get("Node") == "quad-tree":
                    return quad_tree_value(value), expectation
                if isinstance(custom_types, dict) and custom_types.get("Node") == "random-list":
                    return random_list_values(value), expectation
                return node_next_levels(value), expectation
            if isinstance(value, ListNode):
                return list_node_values(value), expectation
            if isinstance(value, TreeNode) or value is None:
                return tree_values(value), expectation
            return value, expectation


        def build_list_node(values):
            if values is None:
                return None
            if isinstance(values, dict) and set(values) == {"values", "cycleTo"}:
                node_values = values.get("values")
                cycle_to = values.get("cycleTo")
                if (
                    not isinstance(node_values, list)
                    or not all(isinstance(item, int) for item in node_values)
                    or not isinstance(cycle_to, int)
                    or cycle_to < 0
                    or cycle_to >= len(node_values)
                ):
                    raise ValueError("cyclic ListNode input must include integer values and a valid cycleTo index")
                dummy = ListNode(0)
                current = dummy
                nodes = []
                for value in node_values:
                    current.next = ListNode(value)
                    current = current.next
                    nodes.append(current)
                current.next = nodes[cycle_to]
                return dummy.next
            if not isinstance(values, list) or not all(isinstance(item, int) for item in values):
                raise ValueError("ListNode values must be null, a list of integers, or a cyclic list object")
            dummy = ListNode(0)
            current = dummy
            for value in values:
                current.next = ListNode(value)
                current = current.next
            return dummy.next


        def build_list_node_list(values):
            if not isinstance(values, list):
                raise ValueError("ListNode list input must be a list")
            return [build_list_node(item) for item in values]


        def build_tree(values):
            if values is None or values == []:
                return None
            if not isinstance(values, list) or not all(item is None or type(item) is int for item in values):
                raise ValueError("TreeNode values must be null or a level-order list of integers/nulls")
            if values[0] is None:
                if any(item is not None for item in values[1:]):
                    raise ValueError("TreeNode root cannot be null when descendants are present")
                return None
            root = TreeNode(values[0])
            queue = [root]
            queue_index = 0
            value_index = 1
            while queue_index < len(queue) and value_index < len(values):
                node = queue[queue_index]
                queue_index += 1
                if value_index < len(values):
                    left_value = values[value_index]
                    value_index += 1
                    if left_value is not None:
                        node.left = TreeNode(left_value)
                        queue.append(node.left)
                if value_index < len(values):
                    right_value = values[value_index]
                    value_index += 1
                    if right_value is not None:
                        node.right = TreeNode(right_value)
                        queue.append(node.right)
            if any(item is not None for item in values[value_index:]):
                raise ValueError("TreeNode level-order list contains unreachable non-null values")
            return root


        def build_node_tree(values):
            if values is None or values == []:
                return None
            if not isinstance(values, list) or not all(item is None or type(item) is int for item in values):
                raise ValueError("Node values must be null or a level-order list of integers/nulls")
            if values[0] is None:
                if any(item is not None for item in values[1:]):
                    raise ValueError("Node root cannot be null when descendants are present")
                return None
            root = Node(values[0])
            queue = [root]
            queue_index = 0
            value_index = 1
            while queue_index < len(queue) and value_index < len(values):
                node = queue[queue_index]
                queue_index += 1
                if value_index < len(values):
                    left_value = values[value_index]
                    value_index += 1
                    if left_value is not None:
                        node.left = Node(left_value)
                        queue.append(node.left)
                if value_index < len(values):
                    right_value = values[value_index]
                    value_index += 1
                    if right_value is not None:
                        node.right = Node(right_value)
                        queue.append(node.right)
            if any(item is not None for item in values[value_index:]):
                raise ValueError("Node level-order list contains unreachable non-null values")
            return root


        def build_random_list(values):
            if values == []:
                return None
            if not isinstance(values, list):
                raise ValueError("random-list Node input must be a list")
            nodes = []
            random_indices = []
            for row in values:
                if not isinstance(row, list) or len(row) != 2:
                    raise ValueError("random-list Node rows must be [value, randomIndex]")
                node_value, random_index = row
                if type(node_value) is not int:
                    raise ValueError("random-list Node values must be integers")
                if random_index is not None and (type(random_index) is not int or random_index < 0 or random_index >= len(values)):
                    raise ValueError("random-list Node random indices must be null or in range")
                nodes.append(Node(node_value))
                random_indices.append(random_index)
            for index, node in enumerate(nodes):
                node.next = nodes[index + 1] if index + 1 < len(nodes) else None
                random_index = random_indices[index]
                node.random = nodes[random_index] if random_index is not None else None
            return nodes[0] if nodes else None


        def build_graph(adjacency):
            if adjacency == []:
                return None
            if not isinstance(adjacency, list):
                raise ValueError("graph Node input must be an adjacency list")
            nodes = [Node(index + 1) for index in range(len(adjacency))]
            for index, neighbors in enumerate(adjacency):
                if not isinstance(neighbors, list):
                    raise ValueError("graph Node neighbors must be lists")
                seen_neighbors = set()
                for neighbor in neighbors:
                    if type(neighbor) is not int or neighbor < 1 or neighbor > len(nodes) or neighbor in seen_neighbors:
                        raise ValueError("graph Node neighbor ids must be unique and in range")
                    seen_neighbors.add(neighbor)
                    nodes[index].neighbors.append(nodes[neighbor - 1])
            reachable = graph_nodes(nodes[0])
            if len(reachable) != len(nodes):
                raise ValueError("graph Node input must be connected from node 1")
            return nodes[0]


        def tree_node_at_path(root, path):
            if root is None:
                raise ValueError("TreeNode reference source is null")
            current = root
            for step in path:
                if step == "L":
                    current = current.left
                elif step == "R":
                    current = current.right
                else:
                    raise ValueError("TreeNode reference path must contain only L/R")
                if current is None:
                    raise ValueError("TreeNode reference path does not resolve")
            return current


        def list_node_values(head):
            if head is None:
                return None
            return [node.val for node in list_node_nodes(head)]


        def tree_values(root):
            if root is None:
                return []
            values = []
            queue = [root]
            queue_index = 0
            seen = set()
            while queue_index < len(queue):
                node = queue[queue_index]
                queue_index += 1
                if node is None:
                    values.append(None)
                    continue
                marker = id(node)
                if marker in seen:
                    raise ValueError("TreeNode output contains a cycle")
                seen.add(marker)
                if type(node.val) is not int:
                    raise ValueError("TreeNode value must be an integer")
                values.append(node.val)
                if len(values) > 10000:
                    raise ValueError("TreeNode output exceeded traversal limit")
                queue.append(node.left)
                queue.append(node.right)
            while values and values[-1] is None:
                values.pop()
            return values


        def node_next_levels(root):
            if root is None:
                return []
            levels = []
            queue = [root]
            seen_tree = set()
            while queue:
                actual_next_nodes = []
                current = queue[0]
                seen_next = set()
                while current is not None:
                    marker = id(current)
                    if marker in seen_next:
                        raise ValueError("Node next chain contains a cycle")
                    seen_next.add(marker)
                    actual_next_nodes.append(current)
                    current = current.next
                if actual_next_nodes != queue:
                    raise ValueError("Node next chain does not match the current level")
                level_values = []
                next_queue = []
                for node in queue:
                    marker = id(node)
                    if marker in seen_tree:
                        raise ValueError("Node tree contains a cycle")
                    seen_tree.add(marker)
                    if type(node.val) is not int:
                        raise ValueError("Node value must be an integer")
                    level_values.append(node.val)
                    if len(seen_tree) > 10000:
                        raise ValueError("Node traversal limit")
                    if node.left is not None:
                        next_queue.append(node.left)
                    if node.right is not None:
                        next_queue.append(node.right)
                levels.append(level_values)
                queue = next_queue
            return levels


        def random_list_nodes(head):
            nodes = []
            seen = set()
            current = head
            while current is not None:
                marker = id(current)
                if marker in seen:
                    raise ValueError("random-list Node next chain contains a cycle")
                seen.add(marker)
                nodes.append(current)
                if len(nodes) > 10000:
                    raise ValueError("random-list Node traversal limit")
                current = current.next
            return nodes


        def random_list_values(head, forbidden_nodes=None):
            nodes = random_list_nodes(head)
            forbidden_ids = {id(node) for node in (forbidden_nodes or [])}
            index_by_id = {}
            for index, node in enumerate(nodes):
                if id(node) in forbidden_ids:
                    raise ValueError("random-list Node output reuses an input node")
                if type(node.val) is not int:
                    raise ValueError("random-list Node value must be an integer")
                index_by_id[id(node)] = index
            values = []
            for node in nodes:
                if node.random is None:
                    random_index = None
                else:
                    random_index = index_by_id.get(id(node.random))
                    if random_index is None:
                        raise ValueError("random-list Node random pointer targets an unknown node")
                values.append([node.val, random_index])
            return values


        def graph_nodes(node):
            if node is None:
                return []
            nodes = []
            seen = set()
            queue = [node]
            queue_index = 0
            while queue_index < len(queue):
                current = queue[queue_index]
                queue_index += 1
                marker = id(current)
                if marker in seen:
                    continue
                seen.add(marker)
                nodes.append(current)
                if len(nodes) > 10000:
                    raise ValueError("graph Node traversal limit")
                if type(current.val) is not int or current.val <= 0:
                    raise ValueError("graph Node value must be a positive integer")
                if not isinstance(current.neighbors, list):
                    raise ValueError("graph Node neighbors must be a list")
                for neighbor in current.neighbors:
                    if neighbor is None:
                        raise ValueError("graph Node neighbor cannot be null")
                    queue.append(neighbor)
            return nodes


        def graph_adjacency_values(node, forbidden_nodes=None):
            if node is None:
                return []
            nodes = graph_nodes(node)
            forbidden_ids = {id(item) for item in (forbidden_nodes or [])}
            by_value = {}
            for current in nodes:
                if id(current) in forbidden_ids:
                    raise ValueError("graph Node output reuses an input node")
                if current.val in by_value:
                    raise ValueError("graph Node values must be unique")
                by_value[current.val] = current
            node_count = len(nodes)
            if set(by_value) != set(range(1, node_count + 1)):
                raise ValueError("graph Node values must be contiguous from 1")
            adjacency = []
            for value in range(1, node_count + 1):
                current = by_value[value]
                row = []
                seen_neighbors = set()
                for neighbor in current.neighbors:
                    if neighbor.val not in by_value:
                        raise ValueError("graph Node neighbor targets an unknown node")
                    if neighbor.val in seen_neighbors:
                        raise ValueError("graph Node duplicate neighbor")
                    seen_neighbors.add(neighbor.val)
                    row.append(neighbor.val)
                adjacency.append(row)
            return adjacency


        def quad_tree_value(node):
            if node is None:
                raise ValueError("quad-tree Node output cannot be null")
            seen = set()

            def serialize(current):
                if current is None:
                    return None
                marker = id(current)
                if marker in seen:
                    raise ValueError("quad-tree Node output contains a cycle")
                seen.add(marker)
                if type(current.val) is not bool or type(current.isLeaf) is not bool:
                    raise ValueError("quad-tree Node val and isLeaf must be booleans")
                children = [current.topLeft, current.topRight, current.bottomLeft, current.bottomRight]
                if current.isLeaf:
                    if any(child is not None for child in children):
                        raise ValueError("quad-tree leaf must not have children")
                else:
                    if any(child is None for child in children):
                        raise ValueError("quad-tree internal node must have four children")
                return {
                    "val": current.val if current.isLeaf else True,
                    "isLeaf": current.isLeaf,
                    "topLeft": serialize(current.topLeft),
                    "topRight": serialize(current.topRight),
                    "bottomLeft": serialize(current.bottomLeft),
                    "bottomRight": serialize(current.bottomRight),
                }

            return serialize(node)


        def canonical_quad_tree_case_value(value):
            if value is None:
                raise ValueError("quad-tree expected value cannot be null")
            if not isinstance(value, dict):
                raise ValueError("quad-tree expected value must be an object")
            required = {"val", "isLeaf", "topLeft", "topRight", "bottomLeft", "bottomRight"}
            if set(value) != required:
                raise ValueError("quad-tree expected value fields")
            if type(value["val"]) is not bool or type(value["isLeaf"]) is not bool:
                raise ValueError("quad-tree expected val and isLeaf must be booleans")
            children = [value["topLeft"], value["topRight"], value["bottomLeft"], value["bottomRight"]]
            if value["isLeaf"]:
                if any(child is not None for child in children):
                    raise ValueError("quad-tree expected leaf children")
            else:
                if any(child is None for child in children):
                    raise ValueError("quad-tree expected internal children")
            return {
                "val": value["val"] if value["isLeaf"] else True,
                "isLeaf": value["isLeaf"],
                "topLeft": None if value["topLeft"] is None else canonical_quad_tree_case_value(value["topLeft"]),
                "topRight": None if value["topRight"] is None else canonical_quad_tree_case_value(value["topRight"]),
                "bottomLeft": None if value["bottomLeft"] is None else canonical_quad_tree_case_value(value["bottomLeft"]),
                "bottomRight": None if value["bottomRight"] is None else canonical_quad_tree_case_value(value["bottomRight"]),
            }


        def list_node_nodes(head):
            if head is None:
                return []
            nodes = []
            seen = set()
            current = head
            while current is not None:
                marker = id(current)
                if marker in seen:
                    raise ValueError("ListNode output contains a cycle")
                seen.add(marker)
                nodes.append(current)
                if len(nodes) > 10000:
                    raise ValueError("ListNode output exceeded traversal limit")
                current = current.next
            return nodes


        def list_node_identity_matches(head, source_nodes, expected_indices):
            actual_nodes = list_node_nodes(head)
            if not isinstance(expected_indices, list):
                raise ValueError("linked-list node indices must be a list")
            expected_nodes = []
            for index in expected_indices:
                if type(index) is not int or index < 0 or index >= len(source_nodes):
                    raise ValueError("linked-list node index is out of range")
                expected_nodes.append(source_nodes[index])
            return actual_nodes == expected_nodes


        def check_linked_list_contract(case, actual, arg_by_name, original_list_nodes, return_type):
            contract = case.get("linkedListContract")
            if not isinstance(contract, dict):
                return []
            errors = []
            result_contract = contract.get("result")
            if result_contract is not None:
                if return_type != "Optional[ListNode]":
                    errors.append("result linked-list contract requires Optional[ListNode] return")
                else:
                    source_name = result_contract.get("from")
                    if source_name not in original_list_nodes:
                        errors.append(f"result linked-list contract references unknown ListNode parameter {source_name}")
                    else:
                        try:
                            matches_result = list_node_identity_matches(
                                actual,
                                original_list_nodes[source_name],
                                result_contract.get("nodeIndices"),
                            )
                        except Exception as exc:
                            errors.append(f"result linked-list contract is invalid: {exc}")
                        else:
                            if not matches_result:
                                errors.append("result linked-list nodes do not match expected input node identities")
            post_call = contract.get("postCall")
            if isinstance(post_call, dict):
                for param_name, expected_indices in post_call.items():
                    if param_name not in original_list_nodes:
                        errors.append(f"post-call linked-list contract references unknown ListNode parameter {param_name}")
                    else:
                        try:
                            matches_post_call = list_node_identity_matches(
                                arg_by_name[param_name],
                                original_list_nodes[param_name],
                                expected_indices,
                            )
                        except Exception as exc:
                            errors.append(f"post-call linked-list contract for {param_name} is invalid: {exc}")
                        else:
                            if not matches_post_call:
                                errors.append(f"post-call linked-list nodes for {param_name} do not match expected input identities")
            return errors


        def linked_list_contract_parameter_names(contract):
            if not isinstance(contract, dict):
                return set()
            names = set()
            result_contract = contract.get("result")
            if isinstance(result_contract, dict) and isinstance(result_contract.get("from"), str):
                names.add(result_contract["from"])
            post_call = contract.get("postCall")
            if isinstance(post_call, dict):
                names.update(name for name in post_call if isinstance(name, str))
            return names

        def driver_value(raw_value, type_name, arg_by_name=None, custom_types=None):
            if type_name == "Optional[ListNode]":
                return build_list_node(raw_value)
            if type_name == "List[Optional[ListNode]]":
                return build_list_node_list(raw_value)
            if type_name == "Optional[Node]":
                if isinstance(custom_types, dict) and custom_types.get("Node") == "graph":
                    return build_graph(raw_value)
                if isinstance(custom_types, dict) and custom_types.get("Node") == "random-list":
                    return build_random_list(raw_value)
                return build_node_tree(raw_value)
            if type_name == "Optional[TreeNode]":
                if isinstance(raw_value, dict) and set(raw_value) == {"from", "path"}:
                    if arg_by_name is None or raw_value["from"] not in arg_by_name:
                        raise ValueError("TreeNode reference source is not available")
                    return tree_node_at_path(arg_by_name[raw_value["from"]], raw_value["path"])
                return build_tree(raw_value)
            return copy.deepcopy(raw_value)


        def comparable_actual(actual, type_name, custom_types=None, forbidden_nodes=None):
            if type_name == "Optional[ListNode]":
                return list_node_values(actual)
            if type_name == "Optional[Node]":
                if isinstance(custom_types, dict) and custom_types.get("Node") == "graph":
                    return graph_adjacency_values(actual, forbidden_nodes)
                if isinstance(custom_types, dict) and custom_types.get("Node") == "quad-tree":
                    return quad_tree_value(actual)
                if isinstance(custom_types, dict) and custom_types.get("Node") == "random-list":
                    return random_list_values(actual, forbidden_nodes)
                return node_next_levels(actual)
            if type_name == "Optional[TreeNode]":
                return tree_values(actual)
            if type_name == "List[Optional[TreeNode]]":
                if not isinstance(actual, list):
                    raise ValueError("TreeNode list output must be a list")
                return [tree_values(tree) for tree in actual]
            return actual


        def expected_matches_return(expected, actual, comparable, return_type, arg_by_name, case, matcher, matcher_config, custom_types=None):
            if return_type == "Optional[TreeNode]" and isinstance(expected, TreeNode):
                return actual is expected
            if return_type == "Optional[Node]" and isinstance(custom_types, dict) and custom_types.get("Node") == "quad-tree":
                expected = canonical_quad_tree_case_value(expected)
            return matches(matcher, comparable, expected, case, matcher_config)


        def method_by_name(methods):
            return {
                method["name"]: method
                for method in methods
                if isinstance(method, dict) and "name" in method
            }


        def operation_args(operation, parameters):
            arg_by_name = {}
            args = []
            for param in parameters:
                value = driver_value(operation["input"][param["name"]], param.get("type"), arg_by_name)
                args.append(value)
                arg_by_name[param["name"]] = value
            return args


        def object_operation_matcher(case_matcher, return_type):
            if case_matcher == "float-tolerance" and return_type not in ("float", "List[float]"):
                return "exact"
            if case_matcher == "object-one-of" and return_type != "int":
                return "exact"
            return case_matcher


        def run_object_cases(solution_class, payload, errors):
            cases = payload["cases"]
            matcher_config = cases.get("matcher", {})
            matcher = matcher_config.get("type", "exact")
            constructor = payload.get("constructor") or {"parameters": []}
            methods = method_by_name(payload.get("methods") or [])
            for case in cases.get("cases", []):
                instance = None
                for operation in case.get("operations", []):
                    operation_type = operation.get("type")
                    if operation_type == "constructor":
                        try:
                            instance = solution_class(*operation_args(operation, constructor.get("parameters", [])))
                        except Exception as exc:
                            add_error(errors, f"case {case.get('name', '<unnamed>')} constructor raised {exc}")
                            break
                        if operation.get("expected") is not None:
                            add_error(errors, f"case {case.get('name', '<unnamed>')} constructor expected {operation.get('expected')} got None")
                            break
                        continue
                    if instance is None:
                        add_error(errors, f"case {case.get('name', '<unnamed>')} operation before constructor")
                        break
                    method_name = operation.get("method")
                    method_spec = methods.get(method_name)
                    if method_spec is None:
                        add_error(errors, f"case {case.get('name', '<unnamed>')} operation {method_name} is not defined")
                        break
                    method = getattr(instance, method_name, None)
                    if not callable(method):
                        add_error(errors, f"case {case.get('name', '<unnamed>')} missing callable {method_name}")
                        break
                    try:
                        actual = method(*operation_args(operation, method_spec.get("parameters", [])))
                    except Exception as exc:
                        add_error(errors, f"case {case.get('name', '<unnamed>')} operation {method_name} raised {exc}")
                        break
                    try:
                        comparable = comparable_actual(actual, method_spec.get("returnType"))
                    except Exception as exc:
                        add_error(errors, f"case {case.get('name', '<unnamed>')} operation {method_name} returned invalid value: {exc}")
                        break
                    operation_matcher = object_operation_matcher(matcher, method_spec.get("returnType"))
                    if not object_matches(operation_matcher, comparable, operation.get("expected"), operation, matcher_config):
                        add_error(
                            errors,
                            f"case {case.get('name', '<unnamed>')} operation {method_name} expected {operation.get('expected')} got {comparable}",
                        )
                        break


        def add_error(errors, message):
            errors.append(message)


        def main():
            solution_path = Path(sys.argv[1])
            payload_path = Path(sys.argv[2])
            result_path = Path(sys.argv[3])
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            global Node
            Node = node_class_for_custom_types(payload.get("customTypes"))
            errors = []
            try:
                module_name = f"coding_solution_{uuid.uuid4().hex}"
                spec = importlib.util.spec_from_file_location(module_name, solution_path)
                if spec is None or spec.loader is None:
                    add_error(errors, "could not load Python solution")
                else:
                    module = importlib.util.module_from_spec(spec)
                    module.ListNode = ListNode
                    module.Node = Node
                    module.TreeNode = TreeNode
                    module.List = List
                    module.Optional = Optional
                    spec.loader.exec_module(module)
                    solution_class = getattr(module, payload["className"], None)
                    if solution_class is None:
                        add_error(errors, f"missing class {payload['className']}")
                    elif payload.get("kind") == "object":
                        run_object_cases(solution_class, payload, errors)
                    else:
                        instance = solution_class()
                        method = getattr(instance, payload["methodName"], None)
                        if not callable(method):
                            add_error(errors, f"missing callable {payload['methodName']}")
                        else:
                            cases = payload["cases"]
                            matcher_config = cases.get("matcher", {})
                            matcher = matcher_config.get("type", "exact")
                            custom_types = payload.get("customTypes") or {}
                            parameter_types = {
                                param["name"]: param.get("type")
                                for param in payload.get("parameters", [])
                                if isinstance(param, dict) and "name" in param
                            }
                            for case in cases.get("cases", []):
                                args = []
                                arg_by_name = {}
                                original_list_nodes = {}
                                original_random_nodes = {}
                                list_contract_names = linked_list_contract_parameter_names(case.get("linkedListContract"))
                                for param in payload.get("parameters", []):
                                    value = driver_value(case["input"][param["name"]], param.get("type"), arg_by_name, custom_types)
                                    args.append(value)
                                    arg_by_name[param["name"]] = value
                                    if param.get("type") == "Optional[ListNode]" and param["name"] in list_contract_names:
                                        original_list_nodes[param["name"]] = list_node_nodes(value)
                                    if param.get("type") == "Optional[Node]" and custom_types.get("Node") == "graph":
                                        original_random_nodes[param["name"]] = graph_nodes(value)
                                    if param.get("type") == "Optional[Node]" and custom_types.get("Node") == "random-list":
                                        original_random_nodes[param["name"]] = random_list_nodes(value)
                                expected_value = case["expected"]
                                if payload.get("returnType") == "Optional[TreeNode]" and isinstance(expected_value, dict) and set(expected_value) == {"from", "path"}:
                                    try:
                                        expected_value = tree_node_at_path(arg_by_name[expected_value["from"]], expected_value["path"])
                                    except Exception as exc:
                                        add_error(errors, f"case {case.get('name', '<unnamed>')} expected reference invalid: {exc}")
                                        continue
                                try:
                                    actual = method(*args)
                                except Exception as exc:
                                    add_error(errors, f"case {case.get('name', '<unnamed>')} raised {exc}")
                                    continue
                                try:
                                    forbidden_random_nodes = []
                                    if payload.get("returnType") == "Optional[Node]" and custom_types.get("Node") in {"graph", "random-list"}:
                                        for nodes in original_random_nodes.values():
                                            forbidden_random_nodes.extend(nodes)
                                    comparable = comparable_actual(actual, payload.get("returnType"), custom_types, forbidden_random_nodes)
                                except Exception as exc:
                                    if payload.get("returnType") == "Optional[ListNode]":
                                        structure_name = "ListNode"
                                    elif payload.get("returnType") == "Optional[Node]":
                                        structure_name = "Node"
                                    elif payload.get("returnType") in {"Optional[TreeNode]", "List[Optional[TreeNode]]"}:
                                        structure_name = "TreeNode"
                                    else:
                                        structure_name = "node structure"
                                    add_error(errors, f"case {case.get('name', '<unnamed>')} returned invalid {structure_name}: {exc}")
                                    continue
                                try:
                                    expected_matches = expected_matches_return(
                                        expected_value,
                                        actual,
                                        comparable,
                                        payload.get("returnType"),
                                        arg_by_name,
                                        case,
                                        matcher,
                                        matcher_config,
                                        custom_types,
                                    )
                                except Exception as exc:
                                    add_error(errors, f"case {case.get('name', '<unnamed>')} expected reference invalid: {exc}")
                                    continue
                                if not expected_matches:
                                    add_error(
                                        errors,
                                        f"case {case.get('name', '<unnamed>')} expected {case['expected']} got {comparable}",
                                    )
                                    continue
                                for contract_error in check_linked_list_contract(
                                    case,
                                    actual,
                                    arg_by_name,
                                    original_list_nodes,
                                    payload.get("returnType"),
                                ):
                                    add_error(errors, f"case {case.get('name', '<unnamed>')} {contract_error}")
                                for param_name, expectation in case.get("expectedMutations", {}).items():
                                    try:
                                        actual_mutation, expected_mutation = mutation_actual_value(
                                            expectation,
                                            actual,
                                            arg_by_name[param_name],
                                            parameter_types.get(param_name),
                                            custom_types,
                                        )
                                    except Exception as exc:
                                        add_error(
                                            errors,
                                            f"case {case.get('name', '<unnamed>')} mutation {param_name} invalid: {exc}",
                                        )
                                        continue
                                    if actual_mutation != expected_mutation:
                                        add_error(
                                            errors,
                                            f"case {case.get('name', '<unnamed>')} expected mutation {param_name} "
                                            f"{expected_mutation} got {actual_mutation}",
                                        )
            except Exception as exc:
                add_error(errors, f"Python driver failed: {exc}")

            result_path.write_text(json.dumps({"errors": errors}), encoding="utf-8")


        if __name__ == "__main__":
            main()
        """
    )

    with tempfile.TemporaryDirectory(prefix="sdip-python-driver-") as tmp:
        tmp_path = Path(tmp)
        runner_path = tmp_path / "runner.py"
        solution_copy = tmp_path / "solution_under_test.py"
        payload_path = tmp_path / "payload.json"
        result_path = tmp_path / "result.json"
        runner_path.write_text(runner_source, encoding="utf-8")
        solution_copy.write_text(solution_path.read_text(encoding="utf-8"), encoding="utf-8")
        payload_path.write_text(json.dumps(payload), encoding="utf-8")
        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONIOENCODING": "utf-8",
        }
        try:
            result = run_driver_command(
                [sys.executable, "-B", str(runner_path), str(solution_copy), str(payload_path), str(result_path)],
                cwd=tmp_path,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=DRIVER_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return [error(solution_path, f"Python driver timed out after {DRIVER_TIMEOUT_SECONDS}s")]

        if result.returncode != 0:
            return [error(solution_path, f"Python driver exited with status {result.returncode}")]
        if not result_path.is_file():
            return [error(solution_path, "Python driver did not write a result")]

        result_payload = json.loads(result_path.read_text(encoding="utf-8"))
        return [error(solution_path, message) for message in result_payload.get("errors", [])]


def run_java_drivers(record: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    toolchain_error = java_toolchain_error()
    if toolchain_error is not None:
        return [error(record["dir"], toolchain_error)]

    problem_dir = Path(record["dir"])
    problem = record["problem"]
    cases = record["cases"] or {}
    solutions = (record["solutions"] or {}).get("solutions", [])
    signature = java_language_signature(problem["signature"])
    if not cases.get("cases"):
        return [error(problem_dir / "cases.json", "driver requires at least one test case")]

    with tempfile.TemporaryDirectory(prefix="sdip-java-driver-") as tmp:
        output_root = Path(tmp)
        for solution in solutions:
            solution_id = solution["id"]
            source_path, message = resolve_solution_path(problem_dir, solution.get("javaPath", ""), "java")
            if message is not None or source_path is None:
                findings.append(error(problem_dir / "solutions.json", f"javaPath {message}"))
                continue

            run_dir = output_root / problem["id"] / solution_id
            class_dir = run_dir / "classes"
            run_dir.mkdir(parents=True, exist_ok=True)
            class_dir.mkdir(parents=True, exist_ok=True)
            solution_copy = run_dir / "Solution.java"
            driver_path = run_dir / "Driver.java"
            try:
                solution_copy.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
                driver_path.write_text(java_driver_source(signature, cases), encoding="utf-8")
            except (OSError, ValueError) as exc:
                findings.append(error(source_path, f"could not prepare Java driver: {exc}"))
                continue

            try:
                compile_result = run_driver_command(
                    ["javac", "-d", str(class_dir), str(solution_copy), str(driver_path)],
                    cwd=run_dir,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env=driver_env(),
                    check=False,
                    timeout=DRIVER_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired:
                findings.append(error(source_path, f"javac timed out after {DRIVER_TIMEOUT_SECONDS}s for {solution_id}"))
                continue
            if compile_result.returncode != 0:
                findings.append(
                    error(source_path, f"javac failed for {solution_id}: {trim_output(compile_result.stdout)}")
                )
                continue

            try:
                run_result = run_driver_command(
                    ["java", "-cp", str(class_dir), "Driver"],
                    cwd=run_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=driver_env(),
                    check=False,
                    timeout=DRIVER_TIMEOUT_SECONDS,
                )
            except subprocess.TimeoutExpired:
                findings.append(error(source_path, f"java driver timed out after {DRIVER_TIMEOUT_SECONDS}s for {solution_id}"))
                continue
            if run_result.returncode != 0:
                findings.append(error(source_path, f"java driver failed for {solution_id}"))

    return findings


def java_toolchain_error() -> str | None:
    if shutil.which("javac") is None or shutil.which("java") is None:
        return "Java toolchain is not available"
    for command in (["javac", "-version"], ["java", "-version"]):
        result = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=driver_env(),
            check=False,
            timeout=DRIVER_TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            return f"Java toolchain is not available: {trim_output(result.stdout)}"
        major_version = java_major_version(result.stdout)
        if major_version is None:
            return f"Java toolchain version could not be parsed: {trim_output(result.stdout)}"
        if major_version < MIN_JAVA_MAJOR_VERSION:
            return (
                f"Java toolchain must be Java {MIN_JAVA_MAJOR_VERSION}+; "
                f"{command[0]} reported Java {major_version}: {trim_output(result.stdout)}"
            )
    return None


def java_major_version(version_output: str) -> int | None:
    match = JAVA_VERSION_PATTERN.search(version_output)
    if match is None:
        return None
    version = match.group("quoted") or match.group("plain")
    parts = version.split(".")
    if not parts or not parts[0].isdigit():
        return None
    first = int(parts[0])
    if first == 1 and len(parts) > 1 and parts[1].isdigit():
        return int(parts[1])
    return first


def run_driver_command(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int,
    check: bool = False,
    stdout: int | None = None,
    stderr: int | None = None,
    text: bool = False,
) -> subprocess.CompletedProcess[str | bytes]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=stdout,
        stderr=stderr,
        text=text,
        start_new_session=True,
    )
    try:
        captured_stdout, captured_stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        terminate_process_group(process)
        process.communicate()
        raise
    result = subprocess.CompletedProcess(command, process.returncode, captured_stdout, captured_stderr)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
    return result


def terminate_process_group(process: subprocess.Popen[str | bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except OSError:
        process.kill()


def driver_env() -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", ""),
        "LC_ALL": "C",
    }


def trim_output(value: str, limit: int = 1200) -> str:
    stripped = value.strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[:limit] + "...<truncated>"


def matches(matcher: str, actual: Any, expected: Any, case: dict[str, Any], matcher_config: dict[str, Any] | None = None) -> bool:
    if matcher == "exact":
        return actual == expected
    if matcher == "unordered-list":
        return canonical_flat_list(actual) == canonical_flat_list(expected)
    if matcher == "unordered-list-of-lists":
        return canonical_nested_list(actual) == canonical_nested_list(expected)
    if matcher == "unordered-tree-list":
        return canonical_nested_list(actual) == canonical_nested_list(expected)
    if matcher == "float-tolerance":
        return float_tolerance_matches(
            actual,
            expected,
            matcher_config.get("tolerance") if isinstance(matcher_config, dict) else None,
        )
    if matcher == "valid-topological-order":
        return valid_topological_order(
            actual,
            case["input"].get("numCourses"),
            case["input"].get("prerequisites"),
        )
    if matcher == "two-sum-indices":
        if not isinstance(actual, list) or len(actual) != 2:
            return False
        nums = case["input"]["nums"]
        target = case["input"]["target"]
        i, j = actual
        return (
            isinstance(i, int)
            and isinstance(j, int)
            and i != j
            and 0 <= i < len(nums)
            and 0 <= j < len(nums)
            and nums[i] + nums[j] == target
        )
    if matcher == "balanced-bst-from-sorted-array":
        return tree_matches_sorted_array(actual, case["input"].get("nums"))
    return actual == expected


def canonical_flat_list(value: Any) -> list[str] | None:
    if not isinstance(value, list):
        return None
    return sorted(json.dumps(item, separators=(",", ":")) for item in value)


def canonical_nested_list(value: Any) -> list[str] | None:
    if not isinstance(value, list):
        return None
    rows = []
    for row in value:
        if not isinstance(row, list):
            return None
        rows.append(json.dumps(row, separators=(",", ":")))
    return sorted(rows)


def is_finite_number(value: Any) -> bool:
    return type(value) in {int, float} and math.isfinite(float(value))


def float_tolerance_matches(actual: Any, expected: Any, tolerance: Any) -> bool:
    if not is_finite_number(tolerance) or tolerance <= 0:
        return False
    if is_finite_number(expected):
        return is_finite_number(actual) and abs(float(actual) - float(expected)) <= float(tolerance)
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            return False
        return all(float_tolerance_matches(left, right, tolerance) for left, right in zip(actual, expected))
    return False


def valid_topological_order(actual: Any, num_courses: Any, prerequisites: Any) -> bool:
    if not valid_topological_input(num_courses, prerequisites):
        return False
    if not isinstance(actual, list) or not all(type(item) is int for item in actual):
        return False
    if len(actual) == 0:
        return num_courses == 0 or not has_topological_order(num_courses, prerequisites)
    if len(actual) != num_courses:
        return False
    position = [-1] * num_courses
    for index, course in enumerate(actual):
        if course < 0 or course >= num_courses or position[course] != -1:
            return False
        position[course] = index
    for edge in prerequisites:
        if (
            not isinstance(edge, list)
            or len(edge) != 2
            or type(edge[0]) is not int
            or type(edge[1]) is not int
            or edge[0] < 0
            or edge[0] >= num_courses
            or edge[1] < 0
            or edge[1] >= num_courses
            or position[edge[1]] >= position[edge[0]]
        ):
            return False
    return True


def valid_topological_input(num_courses: Any, prerequisites: Any) -> bool:
    if type(num_courses) is not int or num_courses < 0:
        return False
    if not isinstance(prerequisites, list):
        return False
    for edge in prerequisites:
        if (
            not isinstance(edge, list)
            or len(edge) != 2
            or type(edge[0]) is not int
            or type(edge[1]) is not int
            or edge[0] < 0
            or edge[0] >= num_courses
            or edge[1] < 0
            or edge[1] >= num_courses
        ):
            return False
    return True


def has_topological_order(num_courses: int, prerequisites: Any) -> bool:
    graph = [[] for _ in range(num_courses)]
    indegree = [0] * num_courses
    for edge in prerequisites:
        graph[edge[1]].append(edge[0])
        indegree[edge[0]] += 1
    queue = [course for course in range(num_courses) if indegree[course] == 0]
    seen = 0
    index = 0
    while index < len(queue):
        course = queue[index]
        index += 1
        seen += 1
        for nxt in graph[course]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return seen == num_courses


def tree_matches_sorted_array(values: Any, nums: Any) -> bool:
    if not isinstance(nums, list) or not all(type(item) is int for item in nums):
        return False
    if values == []:
        return nums == []
    if not isinstance(values, list) or not all(item is None or type(item) is int for item in values):
        return False
    nodes: list[dict[str, Any] | None] = []
    for value in values:
        nodes.append(None if value is None else {"val": value, "left": None, "right": None})
    if not nodes or nodes[0] is None:
        return nums == [] and all(node is None for node in nodes)
    queue = [0]
    queue_index = 0
    value_index = 1
    while queue_index < len(queue) and value_index < len(nodes):
        node_index = queue[queue_index]
        queue_index += 1
        node = nodes[node_index]
        if node is None:
            continue
        if value_index < len(nodes):
            node["left"] = nodes[value_index]
            if nodes[value_index] is not None:
                queue.append(value_index)
            value_index += 1
        if value_index < len(nodes):
            node["right"] = nodes[value_index]
            if nodes[value_index] is not None:
                queue.append(value_index)
            value_index += 1
    if any(node is not None for node in nodes[value_index:]):
        return False
    inorder_values: list[int] = []

    def collect_inorder(node: dict[str, Any] | None) -> None:
        if node is None:
            return
        collect_inorder(node["left"])
        inorder_values.append(node["val"])
        collect_inorder(node["right"])

    def balanced_height(node: dict[str, Any] | None) -> int:
        if node is None:
            return 0
        left_height = balanced_height(node["left"])
        if left_height < 0:
            return -1
        right_height = balanced_height(node["right"])
        if right_height < 0:
            return -1
        if abs(left_height - right_height) > 1:
            return -1
        return max(left_height, right_height) + 1

    collect_inorder(nodes[0])
    return inorder_values == nums and balanced_height(nodes[0]) >= 0


def java_driver_source(signature: dict[str, Any], cases: dict[str, Any]) -> str:
    if signature.get("kind") == "object":
        return java_object_driver_source(signature, cases)

    signature_errors = validate_java_driver_signature(signature, Path("<generated-driver>"))
    if signature_errors:
        raise ValueError("; ".join(finding.message for finding in signature_errors))

    class_name = signature["className"]
    method_name = signature["methodName"]
    return_type = signature["returnType"]
    parameters = signature.get("parameters", [])
    node_kind = signature.get("customTypes", {}).get("Node")
    case_lines = []
    for index, case in enumerate(cases.get("cases", []), start=1):
        declarations = []
        argument_names = []
        input_vars = {}
        for param in parameters:
            variable_name = f"case{index}_{param['name']}"
            declarations.append(
                f"        {param['type']} {variable_name} = {java_literal(case['input'][param['name']], param['type'], input_vars, node_kind)};"
            )
            argument_names.append(variable_name)
            input_vars[param["name"]] = variable_name
        args = ", ".join(argument_names)
        actual_name = f"case{index}_actual"
        matcher_config = cases.get("matcher", {})
        matcher = matcher_config.get("type", "exact")
        parameter_types = {param["name"]: param["type"] for param in parameters}
        case_lines.extend(declarations)
        list_node_snapshots = {}
        node_snapshots = {}
        for param_name in sorted(linked_list_contract_parameter_names(case.get("linkedListContract"))):
            if parameter_types.get(param_name) == "ListNode":
                snapshot_name = f"case{index}_{param_name}_nodes"
                list_node_snapshots[param_name] = snapshot_name
                case_lines.append(f"        ListNode[] {snapshot_name} = listNodes({input_vars[param_name]});")
        if node_kind in {"graph", "random-list"}:
            for param in parameters:
                if param.get("type") == "Node":
                    snapshot_name = f"case{index}_{param['name']}_nodes"
                    node_snapshots[param["name"]] = snapshot_name
                    if node_kind == "graph":
                        case_lines.append(f"        Node[] {snapshot_name} = graphNodes({input_vars[param['name']]});")
                    else:
                        case_lines.append(f"        Node[] {snapshot_name} = randomListNodes({input_vars[param['name']]});")
            forbidden_node_snapshot = java_forbidden_node_snapshot_expression(node_snapshots)
            if len(node_snapshots) > 1:
                case_lines.append(f"        Node[] case{index}_forbidden_nodes = {forbidden_node_snapshot};")
                forbidden_node_snapshot = f"case{index}_forbidden_nodes"
        else:
            forbidden_node_snapshot = None
        if return_type == "void":
            case_lines.append(f"        solution.{method_name}({args});")
            actual_for_mutation = None
            actual_for_contract = None
        else:
            if return_type == "TreeNode" and is_tree_node_reference_value(case["expected"]):
                expected = f"case{index}_expected"
                case_lines.append(f"        TreeNode {expected} = {java_literal(case['expected'], 'TreeNode', input_vars)};")
                check = f"if ({actual_name} != {expected}) throw new AssertionError(\"case {index}\");"
            else:
                expected = java_expected_literal(case["expected"], return_type, node_kind)
                check = java_check_expression(
                    matcher,
                    matcher_config,
                    return_type,
                    actual_name,
                    expected,
                    index,
                    input_vars,
                    node_kind,
                    forbidden_node_snapshot,
                )
            case_lines.append(f"        {return_type} {actual_name} = solution.{method_name}({args});")
            case_lines.append(f"        {check}")
            actual_for_mutation = actual_name
            actual_for_contract = actual_name
        case_lines.extend(
            java_linked_list_contract_check_expressions(
                case.get("linkedListContract"),
                actual_for_contract,
                return_type,
                input_vars,
                list_node_snapshots,
                index,
            )
        )
        for param_name, expectation in case.get("expectedMutations", {}).items():
            case_lines.append(
                f"        {java_mutation_check_expression(input_vars[param_name], parameter_types[param_name], expectation, actual_for_mutation, index, node_kind)}"
            )

    uses_binary_tree_next_node = java_signature_uses_binary_tree_next_node(signature)
    uses_graph_node = java_signature_uses_graph_node(signature)
    uses_quad_tree_node = java_signature_uses_quad_tree_node(signature)
    uses_random_list_node = java_signature_uses_random_list_node(signature)
    uses_list_node = java_signature_uses_list_node(signature)
    uses_tree_node = java_signature_uses_tree_node(signature)
    helper_source = ""
    if uses_binary_tree_next_node:
        helper_source += binary_tree_next_node_java_helper_source()
    if uses_graph_node:
        helper_source += graph_node_java_helper_source()
    if uses_quad_tree_node:
        helper_source += quad_tree_node_java_helper_source()
    if uses_random_list_node:
        helper_source += random_list_node_java_helper_source()
    if uses_list_node:
        helper_source += list_node_java_helper_source()
    if uses_tree_node:
        helper_source += tree_node_java_helper_source()
    driver_helpers = ""
    if uses_binary_tree_next_node:
        driver_helpers += binary_tree_next_node_java_driver_methods_source()
    if uses_graph_node:
        driver_helpers += graph_node_java_driver_methods_source()
    if uses_quad_tree_node:
        driver_helpers += quad_tree_node_java_driver_methods_source()
    if uses_random_list_node:
        driver_helpers += random_list_node_java_driver_methods_source()
    if uses_list_node:
        driver_helpers += list_node_java_driver_methods_source()
    if uses_tree_node:
        driver_helpers += tree_node_java_driver_methods_source()
    driver_helpers += nested_list_java_driver_methods_source()
    return (
        "import java.util.*;\n\n"
        + helper_source
        + "class Driver {\n"
        + driver_helpers
        + "    public static void main(String[] args) {\n"
        f"        {class_name} solution = new {class_name}();\n"
        + "\n".join(case_lines)
        + "\n"
        "    }\n"
        "}\n"
    )


def java_object_driver_source(signature: dict[str, Any], cases: dict[str, Any]) -> str:
    signature_errors = validate_java_driver_signature(signature, Path("<generated-driver>"))
    if signature_errors:
        raise ValueError("; ".join(finding.message for finding in signature_errors))

    class_name = signature["className"]
    methods = {
        method["name"]: method
        for method in signature.get("methods", [])
        if isinstance(method, dict) and isinstance(method.get("name"), str)
    }
    constructor = signature.get("constructor", {"parameters": []})
    case_lines = []
    matcher_config = cases.get("matcher", {})
    matcher = matcher_config.get("type", "exact")
    for case_index, case in enumerate(cases.get("cases", []), start=1):
        instance_name = f"case{case_index}_instance"
        for operation_index, operation in enumerate(case.get("operations", []), start=1):
            if operation.get("type") == "constructor":
                args = java_operation_arguments(operation, constructor.get("parameters", []))
                case_lines.append(f"        {class_name} {instance_name} = new {class_name}({args});")
                if operation.get("expected") is not None:
                    raise ValueError("constructor operation expected must be null")
                continue
            method_name = operation.get("method")
            method = methods.get(method_name)
            if method is None:
                raise ValueError(f"object operation {method_name} is not defined")
            args = java_operation_arguments(operation, method.get("parameters", []))
            return_type = method["returnType"]
            if return_type == "void":
                case_lines.append(f"        {instance_name}.{method_name}({args});")
            else:
                actual_name = f"case{case_index}_op{operation_index}_actual"
                operation_matcher = object_operation_matcher(matcher, return_type)
                expected = java_object_expected_literal(operation.get("expected"), return_type, operation_matcher)
                check = java_object_check_expression(
                    operation_matcher,
                    matcher_config,
                    return_type,
                    actual_name,
                    expected,
                    f"{case_index} operation {operation_index}",
                    {},
                )
                case_lines.append(f"        {return_type} {actual_name} = {instance_name}.{method_name}({args});")
                case_lines.append(f"        {check}")

    helper_source = ""
    if java_signature_uses_list_node(signature):
        helper_source += list_node_java_helper_source()
    if java_signature_uses_tree_node(signature):
        helper_source += tree_node_java_helper_source()
    driver_helpers = ""
    if java_signature_uses_list_node(signature):
        driver_helpers += list_node_java_driver_methods_source()
    if java_signature_uses_tree_node(signature):
        driver_helpers += tree_node_java_driver_methods_source()
    driver_helpers += nested_list_java_driver_methods_source()
    return (
        "import java.util.*;\n\n"
        + helper_source
        + "class Driver {\n"
        + driver_helpers
        + "    public static void main(String[] args) {\n"
        + "\n".join(case_lines)
        + "\n"
        "    }\n"
        "}\n"
    )


def java_operation_arguments(operation: dict[str, Any], parameters: list[dict[str, Any]]) -> str:
    return ", ".join(
        java_literal(operation.get("input", {}).get(parameter["name"]), parameter["type"])
        for parameter in parameters
    )


def object_operation_matcher(case_matcher: str, return_type: str | None) -> str:
    if case_matcher == "float-tolerance" and return_type not in {"double", "float", "double[]", "List<Double>"}:
        return "exact"
    if case_matcher == "object-one-of" and return_type != "int":
        return "exact"
    return case_matcher


def java_object_check_expression(
    matcher: str,
    matcher_config: dict[str, Any],
    return_type: str,
    actual: str,
    expected: str,
    index: int | str,
    input_vars: dict[str, str],
) -> str:
    if matcher == "object-one-of" and return_type == "int":
        return f"if (!intArrayContains({expected}, {actual})) throw new AssertionError(\"case {index}\");"
    return java_check_expression(matcher, matcher_config, return_type, actual, expected, index, input_vars)


def validate_java_driver_signature(signature: dict[str, Any], path: Path) -> list[Finding]:
    if signature.get("kind") == "object":
        return validate_java_object_driver_signature(signature, path)

    findings: list[Finding] = []
    class_name = signature.get("className")
    method_name = signature.get("methodName")
    return_type = signature.get("returnType")

    if class_name != "Solution":
        findings.append(error(path, "signature.java.className must be Solution"))
    if not is_safe_identifier(method_name):
        findings.append(error(path, "signature.java.methodName must be a safe identifier"))
    if return_type not in SUPPORTED_JAVA_RETURN_TYPES:
        findings.append(error(path, "signature.java.returnType is not supported by generated drivers"))

    parameters = signature.get("parameters")
    if not isinstance(parameters, list):
        findings.append(error(path, "signature.java.parameters must be a list"))
        return findings
    for parameter in parameters:
        if not isinstance(parameter, dict):
            findings.append(error(path, "signature.java.parameters entries must be objects"))
            continue
        if not is_safe_identifier(parameter.get("name")):
            findings.append(error(path, "signature.java.parameters name must be a safe identifier"))
        if parameter.get("type") not in SUPPORTED_JAVA_PARAMETER_TYPES:
            findings.append(error(path, "signature.java.parameters type is not supported by generated drivers"))
    return findings


def validate_java_object_driver_signature(signature: dict[str, Any], path: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not is_safe_identifier(signature.get("className")):
        findings.append(error(path, "signature.java.className must be a safe identifier"))
    constructor = signature.get("constructor")
    if not isinstance(constructor, dict):
        findings.append(error(path, "signature.java.constructor must be an object"))
    else:
        findings.extend(validate_java_driver_parameters(constructor.get("parameters"), path, "signature.java.constructor.parameters"))
    methods = signature.get("methods")
    if not isinstance(methods, list) or not methods:
        findings.append(error(path, "signature.java.methods must be a non-empty list"))
        return findings
    seen: set[str] = set()
    for method in methods:
        if not isinstance(method, dict):
            findings.append(error(path, "signature.java.methods entries must be objects"))
            continue
        method_name = method.get("name")
        if not is_safe_identifier(method_name):
            findings.append(error(path, "signature.java.methods name must be a safe identifier"))
        elif method_name in seen:
            findings.append(error(path, f"duplicate object method {method_name}"))
        else:
            seen.add(method_name)
        if method.get("returnType") not in SUPPORTED_JAVA_RETURN_TYPES:
            findings.append(error(path, "signature.java.methods returnType is not supported by generated drivers"))
        findings.extend(validate_java_driver_parameters(method.get("parameters"), path, f"signature.java.methods.{method_name}.parameters"))
    return findings


def validate_java_driver_parameters(parameters: Any, path: Path, label: str) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(parameters, list):
        findings.append(error(path, f"{label} must be a list"))
        return findings
    seen: set[str] = set()
    for parameter in parameters:
        if not isinstance(parameter, dict):
            findings.append(error(path, f"{label} entries must be objects"))
            continue
        name = parameter.get("name")
        if not is_safe_identifier(name):
            findings.append(error(path, f"{label} name must be a safe identifier"))
        elif name in seen:
            findings.append(error(path, f"duplicate parameter {name}"))
        else:
            seen.add(name)
        if parameter.get("type") not in SUPPORTED_JAVA_PARAMETER_TYPES:
            findings.append(error(path, f"{label} type is not supported by generated drivers"))
    return findings


def java_signature_uses_list_node(signature: dict[str, Any]) -> bool:
    if signature.get("kind") == "object":
        return java_object_signature_uses_type(signature, "ListNode")
    return signature.get("returnType") == "ListNode" or any(
        isinstance(parameter, dict) and parameter.get("type") in {"ListNode", "ListNode[]"}
        for parameter in signature.get("parameters", [])
    )


def java_signature_uses_tree_node(signature: dict[str, Any]) -> bool:
    if signature.get("kind") == "object":
        return java_object_signature_uses_type(signature, "TreeNode")
    return signature.get("returnType") in {"TreeNode", "List<TreeNode>"} or any(
        isinstance(parameter, dict) and parameter.get("type") == "TreeNode"
        for parameter in signature.get("parameters", [])
    )


def java_signature_uses_binary_tree_next_node(signature: dict[str, Any]) -> bool:
    if signature.get("customTypes", {}).get("Node") != "binary-tree-next":
        return False
    return signature.get("returnType") == "Node" or any(
        isinstance(parameter, dict) and parameter.get("type") == "Node"
        for parameter in signature.get("parameters", [])
    )


def java_signature_uses_random_list_node(signature: dict[str, Any]) -> bool:
    if signature.get("customTypes", {}).get("Node") != "random-list":
        return False
    return signature.get("returnType") == "Node" or any(
        isinstance(parameter, dict) and parameter.get("type") == "Node"
        for parameter in signature.get("parameters", [])
    )


def java_signature_uses_graph_node(signature: dict[str, Any]) -> bool:
    if signature.get("customTypes", {}).get("Node") != "graph":
        return False
    return signature.get("returnType") == "Node" or any(
        isinstance(parameter, dict) and parameter.get("type") == "Node"
        for parameter in signature.get("parameters", [])
    )


def java_signature_uses_quad_tree_node(signature: dict[str, Any]) -> bool:
    if signature.get("customTypes", {}).get("Node") != "quad-tree":
        return False
    return signature.get("returnType") == "Node" or any(
        isinstance(parameter, dict) and parameter.get("type") == "Node"
        for parameter in signature.get("parameters", [])
    )


def java_forbidden_node_snapshot_expression(node_snapshots: dict[str, str]) -> str:
    snapshot_names = [node_snapshots[name] for name in sorted(node_snapshots)]
    if not snapshot_names:
        return "null"
    if len(snapshot_names) == 1:
        return snapshot_names[0]
    return "concatNodeArrays(new Node[][] {" + ", ".join(snapshot_names) + "})"


def java_object_signature_uses_type(signature: dict[str, Any], type_name: str) -> bool:
    def matches_type(actual: Any) -> bool:
        return actual == type_name or (type_name == "ListNode" and actual == "ListNode[]")

    constructor = signature.get("constructor")
    if isinstance(constructor, dict):
        for parameter in constructor.get("parameters", []):
            if isinstance(parameter, dict) and matches_type(parameter.get("type")):
                return True
    for method in signature.get("methods", []):
        if not isinstance(method, dict):
            continue
        if matches_type(method.get("returnType")):
            return True
        for parameter in method.get("parameters", []):
            if isinstance(parameter, dict) and matches_type(parameter.get("type")):
                return True
    return False


def linked_list_contract_parameter_names(contract: Any) -> set[str]:
    if not isinstance(contract, dict):
        return set()
    names: set[str] = set()
    result = contract.get("result")
    if isinstance(result, dict) and isinstance(result.get("from"), str):
        names.add(result["from"])
    post_call = contract.get("postCall")
    if isinstance(post_call, dict):
        names.update(name for name in post_call if isinstance(name, str))
    return names


def list_node_java_helper_source() -> str:
    return (
        "class ListNode {\n"
        "    int val;\n"
        "    ListNode next;\n\n"
        "    ListNode() {}\n\n"
        "    ListNode(int val) {\n"
        "        this.val = val;\n"
        "    }\n\n"
        "    ListNode(int val, ListNode next) {\n"
        "        this.val = val;\n"
        "        this.next = next;\n"
        "    }\n"
        "}\n\n"
    )


def list_node_java_driver_methods_source() -> str:
    return (
        "    private static ListNode buildList(int[] values) {\n"
        "        ListNode dummy = new ListNode(0);\n"
        "        ListNode current = dummy;\n"
        "        for (int value : values) {\n"
        "            current.next = new ListNode(value);\n"
        "            current = current.next;\n"
        "        }\n"
        "        return dummy.next;\n"
        "    }\n\n"
        "    private static ListNode buildCyclicList(int[] values, int cycleTo) {\n"
        "        ListNode dummy = new ListNode(0);\n"
        "        ListNode current = dummy;\n"
        "        ListNode cycleNode = null;\n"
        "        for (int i = 0; i < values.length; i++) {\n"
        "            current.next = new ListNode(values[i]);\n"
        "            current = current.next;\n"
        "            if (i == cycleTo) {\n"
        "                cycleNode = current;\n"
        "            }\n"
        "        }\n"
        "        current.next = cycleNode;\n"
        "        return dummy.next;\n"
        "    }\n\n"
        "    private static ListNode[] listNodes(ListNode node) {\n"
        "        List<ListNode> nodes = new ArrayList<>();\n"
        "        Set<ListNode> seen = Collections.newSetFromMap(new IdentityHashMap<>());\n"
        "        while (node != null) {\n"
        "            if (!seen.add(node)) {\n"
        "                throw new AssertionError(\"ListNode cycle\");\n"
        "            }\n"
        "            nodes.add(node);\n"
        "            if (nodes.size() > 10000) {\n"
        "                throw new AssertionError(\"ListNode traversal limit\");\n"
        "            }\n"
        "            node = node.next;\n"
        "        }\n"
        "        return nodes.toArray(new ListNode[0]);\n"
        "    }\n\n"
        "    private static boolean listIdentityEquals(ListNode node, ListNode[] source, int[] expectedIndices) {\n"
        "        ListNode[] actual = listNodes(node);\n"
        "        if (actual.length != expectedIndices.length) {\n"
        "            return false;\n"
        "        }\n"
        "        for (int i = 0; i < expectedIndices.length; i++) {\n"
        "            int index = expectedIndices[i];\n"
        "            if (index < 0 || index >= source.length || actual[i] != source[index]) {\n"
        "                return false;\n"
        "            }\n"
        "        }\n"
        "        return true;\n"
        "    }\n\n"
        "    private static boolean listEquals(ListNode node, int[] expected) {\n"
        "        int index = 0;\n"
        "        Set<ListNode> seen = Collections.newSetFromMap(new IdentityHashMap<>());\n"
        "        while (node != null && index < expected.length) {\n"
        "            if (!seen.add(node) || node.val != expected[index]) {\n"
        "                return false;\n"
        "            }\n"
        "            node = node.next;\n"
        "            index++;\n"
        "        }\n"
        "        return node == null && index == expected.length;\n"
        "    }\n\n"
    )


def tree_node_java_helper_source() -> str:
    return (
        "class TreeNode {\n"
        "    int val;\n"
        "    TreeNode left;\n"
        "    TreeNode right;\n\n"
        "    TreeNode() {}\n\n"
        "    TreeNode(int val) {\n"
        "        this.val = val;\n"
        "    }\n\n"
        "    TreeNode(int val, TreeNode left, TreeNode right) {\n"
        "        this.val = val;\n"
        "        this.left = left;\n"
        "        this.right = right;\n"
        "    }\n"
        "}\n\n"
    )


def binary_tree_next_node_java_helper_source() -> str:
    return (
        "class Node {\n"
        "    public int val;\n"
        "    public Node left;\n"
        "    public Node right;\n"
        "    public Node next;\n\n"
        "    public Node() {}\n\n"
        "    public Node(int val) {\n"
        "        this.val = val;\n"
        "    }\n\n"
        "    public Node(int val, Node left, Node right, Node next) {\n"
        "        this.val = val;\n"
        "        this.left = left;\n"
        "        this.right = right;\n"
        "        this.next = next;\n"
        "    }\n"
        "}\n\n"
    )


def binary_tree_next_node_java_driver_methods_source() -> str:
    return (
        "    private static Node buildNodeTree(Integer[] values) {\n"
        "        if (values.length == 0) {\n"
        "            return null;\n"
        "        }\n"
        "        if (values[0] == null) {\n"
        "            for (int i = 1; i < values.length; i++) {\n"
        "                if (values[i] != null) {\n"
        "                    throw new AssertionError(\"Node unreachable value\");\n"
        "                }\n"
        "            }\n"
        "            return null;\n"
        "        }\n"
        "        Node root = new Node(values[0]);\n"
        "        Queue<Node> queue = new ArrayDeque<>();\n"
        "        queue.add(root);\n"
        "        int index = 1;\n"
        "        while (!queue.isEmpty() && index < values.length) {\n"
        "            Node node = queue.remove();\n"
        "            Integer leftValue = values[index++];\n"
        "            if (leftValue != null) {\n"
        "                node.left = new Node(leftValue);\n"
        "                queue.add(node.left);\n"
        "            }\n"
        "            if (index < values.length) {\n"
        "                Integer rightValue = values[index++];\n"
        "                if (rightValue != null) {\n"
        "                    node.right = new Node(rightValue);\n"
        "                    queue.add(node.right);\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "        while (index < values.length) {\n"
        "            if (values[index++] != null) {\n"
        "                throw new AssertionError(\"Node unreachable value\");\n"
        "            }\n"
        "        }\n"
        "        return root;\n"
        "    }\n\n"
        "    private static List<List<Integer>> nodeNextLevels(Node root) {\n"
        "        List<List<Integer>> levels = new ArrayList<>();\n"
        "        if (root == null) {\n"
        "            return levels;\n"
        "        }\n"
        "        List<Node> level = new ArrayList<>();\n"
        "        level.add(root);\n"
        "        Set<Node> seenTree = Collections.newSetFromMap(new IdentityHashMap<>());\n"
        "        while (!level.isEmpty()) {\n"
        "            List<Node> actualNext = new ArrayList<>();\n"
        "            Set<Node> seenNext = Collections.newSetFromMap(new IdentityHashMap<>());\n"
        "            Node current = level.get(0);\n"
        "            while (current != null) {\n"
        "                if (!seenNext.add(current)) {\n"
        "                    throw new AssertionError(\"Node next cycle\");\n"
        "                }\n"
        "                actualNext.add(current);\n"
        "                current = current.next;\n"
        "            }\n"
        "            if (!actualNext.equals(level)) {\n"
        "                throw new AssertionError(\"Node next chain mismatch\");\n"
        "            }\n"
        "            List<Integer> values = new ArrayList<>();\n"
        "            List<Node> nextLevel = new ArrayList<>();\n"
        "            for (Node node : level) {\n"
        "                if (!seenTree.add(node)) {\n"
        "                    throw new AssertionError(\"Node tree cycle\");\n"
        "                }\n"
        "                values.add(node.val);\n"
        "                if (seenTree.size() > 10000) {\n"
        "                    throw new AssertionError(\"Node traversal limit\");\n"
        "                }\n"
        "                if (node.left != null) {\n"
        "                    nextLevel.add(node.left);\n"
        "                }\n"
        "                if (node.right != null) {\n"
        "                    nextLevel.add(node.right);\n"
        "                }\n"
        "            }\n"
        "            levels.add(values);\n"
        "            level = nextLevel;\n"
        "        }\n"
        "        return levels;\n"
        "    }\n\n"
    )


def random_list_node_java_helper_source() -> str:
    return (
        "class Node {\n"
        "    int val;\n"
        "    Node next;\n"
        "    Node random;\n\n"
        "    public Node(int val) {\n"
        "        this.val = val;\n"
        "    }\n"
        "}\n\n"
    )


def quad_tree_node_java_helper_source() -> str:
    return (
        "class Node {\n"
        "    public boolean val;\n"
        "    public boolean isLeaf;\n"
        "    public Node topLeft;\n"
        "    public Node topRight;\n"
        "    public Node bottomLeft;\n"
        "    public Node bottomRight;\n\n"
        "    public Node() {}\n\n"
        "    public Node(boolean val, boolean isLeaf) {\n"
        "        this.val = val;\n"
        "        this.isLeaf = isLeaf;\n"
        "    }\n\n"
        "    public Node(boolean val, boolean isLeaf, Node topLeft, Node topRight, Node bottomLeft, Node bottomRight) {\n"
        "        this.val = val;\n"
        "        this.isLeaf = isLeaf;\n"
        "        this.topLeft = topLeft;\n"
        "        this.topRight = topRight;\n"
        "        this.bottomLeft = bottomLeft;\n"
        "        this.bottomRight = bottomRight;\n"
        "    }\n"
        "}\n\n"
    )


def graph_node_java_helper_source() -> str:
    return (
        "class Node {\n"
        "    public int val;\n"
        "    public List<Node> neighbors;\n\n"
        "    public Node() {\n"
        "        val = 0;\n"
        "        neighbors = new ArrayList<>();\n"
        "    }\n\n"
        "    public Node(int val) {\n"
        "        this.val = val;\n"
        "        neighbors = new ArrayList<>();\n"
        "    }\n\n"
        "    public Node(int val, ArrayList<Node> neighbors) {\n"
        "        this.val = val;\n"
        "        this.neighbors = neighbors;\n"
        "    }\n"
        "}\n\n"
    )


def graph_node_java_driver_methods_source() -> str:
    return (
        "    private static Node buildGraph(int[][] adjacency) {\n"
        "        if (adjacency.length == 0) {\n"
        "            return null;\n"
        "        }\n"
        "        Node[] nodes = new Node[adjacency.length];\n"
        "        for (int i = 0; i < adjacency.length; i++) {\n"
        "            nodes[i] = new Node(i + 1);\n"
        "        }\n"
        "        for (int i = 0; i < adjacency.length; i++) {\n"
        "            Set<Integer> seen = new HashSet<>();\n"
        "            for (int neighbor : adjacency[i]) {\n"
        "                if (neighbor < 1 || neighbor > adjacency.length || !seen.add(neighbor)) {\n"
        "                    throw new AssertionError(\"graph neighbor index\");\n"
        "                }\n"
        "                nodes[i].neighbors.add(nodes[neighbor - 1]);\n"
        "            }\n"
        "        }\n"
        "        if (graphNodes(nodes[0]).length != nodes.length) {\n"
        "            throw new AssertionError(\"graph must be connected from node 1\");\n"
        "        }\n"
        "        return nodes[0];\n"
        "    }\n\n"
        "    private static Node[] graphNodes(Node node) {\n"
        "        if (node == null) {\n"
        "            return new Node[0];\n"
        "        }\n"
        "        List<Node> nodes = new ArrayList<>();\n"
        "        Set<Node> seen = Collections.newSetFromMap(new IdentityHashMap<>());\n"
        "        Queue<Node> queue = new ArrayDeque<>();\n"
        "        queue.add(node);\n"
        "        while (!queue.isEmpty()) {\n"
        "            Node current = queue.remove();\n"
        "            if (!seen.add(current)) {\n"
        "                continue;\n"
        "            }\n"
        "            if (current.val <= 0 || current.neighbors == null) {\n"
        "                throw new AssertionError(\"graph node shape\");\n"
        "            }\n"
        "            nodes.add(current);\n"
        "            if (nodes.size() > 10000) {\n"
        "                throw new AssertionError(\"graph traversal limit\");\n"
        "            }\n"
        "            for (Node neighbor : current.neighbors) {\n"
        "                if (neighbor == null) {\n"
        "                    throw new AssertionError(\"graph null neighbor\");\n"
        "                }\n"
        "                queue.add(neighbor);\n"
        "            }\n"
        "        }\n"
        "        return nodes.toArray(new Node[0]);\n"
        "    }\n\n"
        "    private static List<List<Integer>> graphAdjacencyValues(Node node, Node[] forbidden) {\n"
        "        Node[] nodes = graphNodes(node);\n"
        "        Set<Node> forbiddenNodes = Collections.newSetFromMap(new IdentityHashMap<>());\n"
        "        if (forbidden != null) {\n"
        "            forbiddenNodes.addAll(Arrays.asList(forbidden));\n"
        "        }\n"
        "        Map<Integer, Node> byValue = new HashMap<>();\n"
        "        for (Node current : nodes) {\n"
        "            if (forbiddenNodes.contains(current)) {\n"
        "                throw new AssertionError(\"graph reused input node\");\n"
        "            }\n"
        "            if (byValue.put(current.val, current) != null) {\n"
        "                throw new AssertionError(\"graph duplicate value\");\n"
        "            }\n"
        "        }\n"
        "        for (int value = 1; value <= nodes.length; value++) {\n"
        "            if (!byValue.containsKey(value)) {\n"
        "                throw new AssertionError(\"graph values must be contiguous\");\n"
        "            }\n"
        "        }\n"
        "        List<List<Integer>> adjacency = new ArrayList<>();\n"
        "        for (int value = 1; value <= nodes.length; value++) {\n"
        "            Node current = byValue.get(value);\n"
        "            List<Integer> row = new ArrayList<>();\n"
        "            Set<Integer> seen = new HashSet<>();\n"
        "            for (Node neighbor : current.neighbors) {\n"
        "                if (!byValue.containsKey(neighbor.val) || !seen.add(neighbor.val)) {\n"
        "                    throw new AssertionError(\"graph neighbor value\");\n"
        "                }\n"
        "                row.add(neighbor.val);\n"
        "            }\n"
        "            adjacency.add(row);\n"
        "        }\n"
        "        return adjacency;\n"
        "    }\n\n"
        "    private static Node[] concatNodeArrays(Node[][] arrays) {\n"
        "        List<Node> nodes = new ArrayList<>();\n"
        "        for (Node[] array : arrays) {\n"
        "            if (array != null) {\n"
        "                nodes.addAll(Arrays.asList(array));\n"
        "            }\n"
        "        }\n"
        "        return nodes.toArray(new Node[0]);\n"
        "    }\n\n"
    )


def quad_tree_node_java_driver_methods_source() -> str:
    return (
        "    private static String quadTreeSignature(Node node) {\n"
        "        Set<Node> seen = Collections.newSetFromMap(new IdentityHashMap<>());\n"
        "        return quadTreeSignature(node, seen);\n"
        "    }\n\n"
        "    private static String quadTreeSignature(Node node, Set<Node> seen) {\n"
        "        if (node == null) {\n"
        "            return \"null\";\n"
        "        }\n"
        "        if (!seen.add(node)) {\n"
        "            throw new AssertionError(\"quad-tree cycle\");\n"
        "        }\n"
        "        if (node.isLeaf) {\n"
        "            if (node.topLeft != null || node.topRight != null || node.bottomLeft != null || node.bottomRight != null) {\n"
        "                throw new AssertionError(\"quad-tree leaf children\");\n"
        "            }\n"
        "        } else if (node.topLeft == null || node.topRight == null || node.bottomLeft == null || node.bottomRight == null) {\n"
        "            throw new AssertionError(\"quad-tree internal children\");\n"
        "        }\n"
        "        return \"{\\\"val\\\":\" + (node.isLeaf ? node.val : true)\n"
        "            + \",\\\"isLeaf\\\":\" + node.isLeaf\n"
        "            + \",\\\"topLeft\\\":\" + quadTreeSignature(node.topLeft, seen)\n"
        "            + \",\\\"topRight\\\":\" + quadTreeSignature(node.topRight, seen)\n"
        "            + \",\\\"bottomLeft\\\":\" + quadTreeSignature(node.bottomLeft, seen)\n"
        "            + \",\\\"bottomRight\\\":\" + quadTreeSignature(node.bottomRight, seen)\n"
        "            + \"}\";\n"
        "    }\n\n"
    )


def random_list_node_java_driver_methods_source() -> str:
    return (
        "    private static Node buildRandomList(int[] values, int[] randomIndices) {\n"
        "        if (values.length != randomIndices.length) {\n"
        "            throw new AssertionError(\"random-list length mismatch\");\n"
        "        }\n"
        "        if (values.length == 0) {\n"
        "            return null;\n"
        "        }\n"
        "        Node[] nodes = new Node[values.length];\n"
        "        for (int i = 0; i < values.length; i++) {\n"
        "            nodes[i] = new Node(values[i]);\n"
        "        }\n"
        "        for (int i = 0; i < values.length; i++) {\n"
        "            nodes[i].next = i + 1 < values.length ? nodes[i + 1] : null;\n"
        "            int randomIndex = randomIndices[i];\n"
        "            if (randomIndex == -1) {\n"
        "                nodes[i].random = null;\n"
        "            } else if (randomIndex >= 0 && randomIndex < values.length) {\n"
        "                nodes[i].random = nodes[randomIndex];\n"
        "            } else {\n"
        "                throw new AssertionError(\"random-list random index\");\n"
        "            }\n"
        "        }\n"
        "        return nodes[0];\n"
        "    }\n\n"
        "    private static Node[] randomListNodes(Node head) {\n"
        "        List<Node> nodes = new ArrayList<>();\n"
        "        Set<Node> seen = Collections.newSetFromMap(new IdentityHashMap<>());\n"
        "        Node current = head;\n"
        "        while (current != null) {\n"
        "            if (!seen.add(current)) {\n"
        "                throw new AssertionError(\"random-list next cycle\");\n"
        "            }\n"
        "            nodes.add(current);\n"
        "            if (nodes.size() > 10000) {\n"
        "                throw new AssertionError(\"random-list traversal limit\");\n"
        "            }\n"
        "            current = current.next;\n"
        "        }\n"
        "        return nodes.toArray(new Node[0]);\n"
        "    }\n\n"
        "    private static List<List<Integer>> randomListValues(Node head, Node[] forbidden) {\n"
        "        Node[] nodes = randomListNodes(head);\n"
        "        Set<Node> forbiddenNodes = Collections.newSetFromMap(new IdentityHashMap<>());\n"
        "        if (forbidden != null) {\n"
        "            forbiddenNodes.addAll(Arrays.asList(forbidden));\n"
        "        }\n"
        "        Map<Node, Integer> indexByNode = new IdentityHashMap<>();\n"
        "        for (int i = 0; i < nodes.length; i++) {\n"
        "            if (forbiddenNodes.contains(nodes[i])) {\n"
        "                throw new AssertionError(\"random-list reused input node\");\n"
        "            }\n"
        "            indexByNode.put(nodes[i], i);\n"
        "        }\n"
        "        List<List<Integer>> values = new ArrayList<>();\n"
        "        for (Node node : nodes) {\n"
        "            Integer randomIndex = null;\n"
        "            if (node.random != null) {\n"
        "                randomIndex = indexByNode.get(node.random);\n"
        "                if (randomIndex == null) {\n"
        "                    throw new AssertionError(\"random-list random target\");\n"
        "                }\n"
        "            }\n"
        "            values.add(Arrays.asList(node.val, randomIndex));\n"
        "        }\n"
        "        return values;\n"
        "    }\n\n"
        "    private static Node[] concatNodeArrays(Node[][] arrays) {\n"
        "        List<Node> nodes = new ArrayList<>();\n"
        "        for (Node[] array : arrays) {\n"
        "            if (array != null) {\n"
        "                nodes.addAll(Arrays.asList(array));\n"
        "            }\n"
        "        }\n"
        "        return nodes.toArray(new Node[0]);\n"
        "    }\n\n"
    )


def tree_node_java_driver_methods_source() -> str:
    return (
        "    private static TreeNode buildTree(Integer[] values) {\n"
        "        if (values.length == 0) {\n"
        "            return null;\n"
        "        }\n"
        "        if (values[0] == null) {\n"
        "            for (int i = 1; i < values.length; i++) {\n"
        "                if (values[i] != null) {\n"
        "                    throw new AssertionError(\"TreeNode unreachable value\");\n"
        "                }\n"
        "            }\n"
        "            return null;\n"
        "        }\n"
        "        TreeNode root = new TreeNode(values[0]);\n"
        "        Queue<TreeNode> queue = new ArrayDeque<>();\n"
        "        queue.add(root);\n"
        "        int index = 1;\n"
        "        while (!queue.isEmpty() && index < values.length) {\n"
        "            TreeNode node = queue.remove();\n"
        "            Integer leftValue = values[index++];\n"
        "            if (leftValue != null) {\n"
        "                node.left = new TreeNode(leftValue);\n"
        "                queue.add(node.left);\n"
        "            }\n"
        "            if (index < values.length) {\n"
        "                Integer rightValue = values[index++];\n"
        "                if (rightValue != null) {\n"
        "                    node.right = new TreeNode(rightValue);\n"
        "                    queue.add(node.right);\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "        while (index < values.length) {\n"
        "            if (values[index++] != null) {\n"
        "                throw new AssertionError(\"TreeNode unreachable value\");\n"
        "            }\n"
        "        }\n"
        "        return root;\n"
        "    }\n\n"
        "    private static TreeNode treeNodeAtPath(TreeNode root, String path) {\n"
        "        if (root == null) {\n"
        "            throw new AssertionError(\"TreeNode reference source is null\");\n"
        "        }\n"
        "        TreeNode current = root;\n"
        "        for (int i = 0; i < path.length(); i++) {\n"
        "            char step = path.charAt(i);\n"
        "            if (step == 'L') {\n"
        "                current = current.left;\n"
        "            } else if (step == 'R') {\n"
        "                current = current.right;\n"
        "            } else {\n"
        "                throw new AssertionError(\"TreeNode reference path\");\n"
        "            }\n"
        "            if (current == null) {\n"
        "                throw new AssertionError(\"TreeNode reference path\");\n"
        "            }\n"
        "        }\n"
        "        return current;\n"
        "    }\n\n"
        "    private static List<Integer> treeValues(TreeNode root) {\n"
        "        if (root == null) {\n"
        "            return Collections.emptyList();\n"
        "        }\n"
        "        List<Integer> values = new ArrayList<>();\n"
        "        Queue<TreeNode> queue = new LinkedList<>();\n"
        "        Set<TreeNode> seen = Collections.newSetFromMap(new IdentityHashMap<>());\n"
        "        queue.add(root);\n"
        "        while (!queue.isEmpty()) {\n"
        "            TreeNode node = queue.remove();\n"
        "            if (node == null) {\n"
        "                values.add(null);\n"
        "                continue;\n"
        "            }\n"
        "            if (!seen.add(node)) {\n"
        "                throw new AssertionError(\"TreeNode cycle\");\n"
        "            }\n"
        "            values.add(node.val);\n"
        "            if (values.size() > 10000) {\n"
        "                throw new AssertionError(\"TreeNode traversal limit\");\n"
        "            }\n"
        "            queue.add(node.left);\n"
        "            queue.add(node.right);\n"
        "        }\n"
        "        while (!values.isEmpty() && values.get(values.size() - 1) == null) {\n"
        "            values.remove(values.size() - 1);\n"
        "        }\n"
        "        return values;\n"
        "    }\n\n"
        "    private static boolean unorderedTreeListEquals(List<TreeNode> actual, List<TreeNode> expected) {\n"
        "        return Objects.equals(canonicalTreeList(actual), canonicalTreeList(expected));\n"
        "    }\n\n"
        "    private static List<String> canonicalTreeList(List<TreeNode> trees) {\n"
        "        if (trees == null) {\n"
        "            return null;\n"
        "        }\n"
        "        List<String> canonical = new ArrayList<>();\n"
        "        for (TreeNode tree : trees) {\n"
        "            canonical.add(treeValues(tree).toString());\n"
        "        }\n"
        "        Collections.sort(canonical);\n"
        "        return canonical;\n"
        "    }\n\n"
        "    private static boolean balancedBstMatchesSortedArray(TreeNode root, int[] nums) {\n"
        "        if (root == null) {\n"
        "            return nums.length == 0;\n"
        "        }\n"
        "        if (balancedHeight(root, Collections.newSetFromMap(new IdentityHashMap<>())) < 0) {\n"
        "            return false;\n"
        "        }\n"
        "        List<Integer> values = new ArrayList<>();\n"
        "        if (!collectInorder(root, values, Collections.newSetFromMap(new IdentityHashMap<>()))) {\n"
        "            return false;\n"
        "        }\n"
        "        if (values.size() != nums.length) {\n"
        "            return false;\n"
        "        }\n"
        "        for (int i = 0; i < nums.length; i++) {\n"
        "            if (!Objects.equals(values.get(i), nums[i])) {\n"
        "                return false;\n"
        "            }\n"
        "        }\n"
        "        return true;\n"
        "    }\n\n"
        "    private static boolean collectInorder(TreeNode node, List<Integer> values, Set<TreeNode> seen) {\n"
        "        if (node == null) {\n"
        "            return true;\n"
        "        }\n"
        "        if (!seen.add(node) || seen.size() > 10000) {\n"
        "            return false;\n"
        "        }\n"
        "        if (!collectInorder(node.left, values, seen)) {\n"
        "            return false;\n"
        "        }\n"
        "        values.add(node.val);\n"
        "        return collectInorder(node.right, values, seen);\n"
        "    }\n\n"
        "    private static int balancedHeight(TreeNode node, Set<TreeNode> seen) {\n"
        "        if (node == null) {\n"
        "            return 0;\n"
        "        }\n"
        "        if (!seen.add(node) || seen.size() > 10000) {\n"
        "            return -1;\n"
        "        }\n"
        "        int leftHeight = balancedHeight(node.left, seen);\n"
        "        if (leftHeight < 0) {\n"
        "            return -1;\n"
        "        }\n"
        "        int rightHeight = balancedHeight(node.right, seen);\n"
        "        if (rightHeight < 0) {\n"
        "            return -1;\n"
        "        }\n"
        "        if (Math.abs(leftHeight - rightHeight) > 1) {\n"
        "            return -1;\n"
        "        }\n"
        "        return Math.max(leftHeight, rightHeight) + 1;\n"
        "    }\n\n"
    )


def nested_list_java_driver_methods_source() -> str:
    return (
        "    private static boolean floatEquals(double actual, double expected, double tolerance) {\n"
        "        return Double.isFinite(actual) && Double.isFinite(expected) && Math.abs(actual - expected) <= tolerance;\n"
        "    }\n\n"
        "    private static boolean floatListEquals(List<Double> actual, List<Double> expected, double tolerance) {\n"
        "        if (actual == null || expected == null || actual.size() != expected.size()) {\n"
        "            return false;\n"
        "        }\n"
        "        for (int i = 0; i < actual.size(); i++) {\n"
        "            Double left = actual.get(i);\n"
        "            Double right = expected.get(i);\n"
        "            if (left == null || right == null || !floatEquals(left, right, tolerance)) {\n"
        "                return false;\n"
        "            }\n"
        "        }\n"
        "        return true;\n"
        "    }\n\n"
        "    private static boolean intArrayContains(int[] values, int target) {\n"
        "        for (int value : values) {\n"
        "            if (value == target) {\n"
        "                return true;\n"
        "            }\n"
        "        }\n"
        "        return false;\n"
        "    }\n\n"
        "    private static boolean floatListEquals(double[] actual, double[] expected, double tolerance) {\n"
        "        if (actual == null || expected == null || actual.length != expected.length) {\n"
        "            return false;\n"
        "        }\n"
        "        for (int i = 0; i < actual.length; i++) {\n"
        "            if (!floatEquals(actual[i], expected[i], tolerance)) {\n"
        "                return false;\n"
        "            }\n"
        "        }\n"
        "        return true;\n"
        "    }\n\n"
        "    private static <T> boolean unorderedFlatListEquals(List<T> actual, List<T> expected) {\n"
        "        return Objects.equals(canonicalFlatList(actual), canonicalFlatList(expected));\n"
        "    }\n\n"
        "    private static <T> List<String> canonicalFlatList(List<T> value) {\n"
        "        if (value == null) {\n"
        "            return null;\n"
        "        }\n"
        "        List<String> canonical = new ArrayList<>();\n"
        "        for (T item : value) {\n"
        "            String scalar = canonicalScalar(item);\n"
        "            if (scalar == null) {\n"
        "                return null;\n"
        "            }\n"
        "            canonical.add(scalar);\n"
        "        }\n"
        "        Collections.sort(canonical);\n"
        "        return canonical;\n"
        "    }\n\n"
        "    private static boolean unorderedListOfListsEquals(List<? extends List<?>> actual, List<? extends List<?>> expected) {\n"
        "        return Objects.equals(canonicalNestedList(actual), canonicalNestedList(expected));\n"
        "    }\n\n"
        "    private static boolean unorderedIntMatrixEquals(int[][] actual, int[][] expected) {\n"
        "        return Objects.equals(canonicalIntMatrix(actual), canonicalIntMatrix(expected));\n"
        "    }\n\n"
        "    private static List<String> canonicalIntMatrix(int[][] value) {\n"
        "        if (value == null) {\n"
        "            return null;\n"
        "        }\n"
        "        List<String> canonical = new ArrayList<>();\n"
        "        for (int[] row : value) {\n"
        "            if (row == null) {\n"
        "                return null;\n"
        "            }\n"
        "            StringBuilder builder = new StringBuilder();\n"
        "            builder.append('[');\n"
        "            for (int i = 0; i < row.length; i++) {\n"
        "                if (i > 0) {\n"
        "                    builder.append(',');\n"
        "                }\n"
        "                builder.append(canonicalScalar(row[i]));\n"
        "            }\n"
        "            builder.append(']');\n"
        "            canonical.add(builder.toString());\n"
        "        }\n"
        "        Collections.sort(canonical);\n"
        "        return canonical;\n"
        "    }\n\n"
        "    private static List<String> canonicalNestedList(List<? extends List<?>> value) {\n"
        "        if (value == null) {\n"
        "            return null;\n"
        "        }\n"
        "        List<String> canonical = new ArrayList<>();\n"
        "        for (Object rowValue : value) {\n"
        "            if (!(rowValue instanceof List<?>)) {\n"
        "                return null;\n"
        "            }\n"
        "            List<?> row = (List<?>) rowValue;\n"
        "            StringBuilder builder = new StringBuilder();\n"
        "            builder.append('[');\n"
        "            for (int i = 0; i < row.size(); i++) {\n"
        "                Object item = row.get(i);\n"
        "                String scalar = canonicalScalar(item);\n"
        "                if (scalar == null) {\n"
        "                    return null;\n"
        "                }\n"
        "                if (i > 0) {\n"
        "                    builder.append(',');\n"
        "                }\n"
        "                builder.append(scalar);\n"
        "            }\n"
        "            builder.append(']');\n"
        "            canonical.add(builder.toString());\n"
        "        }\n"
        "        Collections.sort(canonical);\n"
        "        return canonical;\n"
        "    }\n\n"
        "    private static String canonicalScalar(Object item) {\n"
        "        if (!(item instanceof Integer) && !(item instanceof String)) {\n"
        "            return null;\n"
        "        }\n"
        "        String value = item.toString();\n"
        "        return item.getClass().getName() + \":\" + value.length() + \":\" + value;\n"
        "    }\n\n"
        "    private static boolean validTopologicalOrder(int[] actual, int numCourses, int[][] prerequisites) {\n"
        "        if (actual == null || !validTopologicalInput(numCourses, prerequisites)) {\n"
        "            return false;\n"
        "        }\n"
        "        if (actual.length == 0) {\n"
        "            return numCourses == 0 || !hasTopologicalOrder(numCourses, prerequisites);\n"
        "        }\n"
        "        if (actual.length != numCourses) {\n"
        "            return false;\n"
        "        }\n"
        "        int[] position = new int[numCourses];\n"
        "        Arrays.fill(position, -1);\n"
        "        for (int i = 0; i < actual.length; i++) {\n"
        "            int course = actual[i];\n"
        "            if (course < 0 || course >= numCourses || position[course] != -1) {\n"
        "                return false;\n"
        "            }\n"
        "            position[course] = i;\n"
        "        }\n"
        "        for (int[] edge : prerequisites) {\n"
        "            if (edge == null || edge.length != 2 || edge[0] < 0 || edge[0] >= numCourses || edge[1] < 0 || edge[1] >= numCourses) {\n"
        "                return false;\n"
        "            }\n"
        "            if (position[edge[1]] >= position[edge[0]]) {\n"
        "                return false;\n"
        "            }\n"
        "        }\n"
        "        return true;\n"
        "    }\n\n"
        "    private static boolean validTopologicalInput(int numCourses, int[][] prerequisites) {\n"
        "        if (numCourses < 0 || prerequisites == null) {\n"
        "            return false;\n"
        "        }\n"
        "        for (int[] edge : prerequisites) {\n"
        "            if (edge == null || edge.length != 2 || edge[0] < 0 || edge[0] >= numCourses || edge[1] < 0 || edge[1] >= numCourses) {\n"
        "                return false;\n"
        "            }\n"
        "        }\n"
        "        return true;\n"
        "    }\n\n"
        "    private static boolean hasTopologicalOrder(int numCourses, int[][] prerequisites) {\n"
        "        List<List<Integer>> graph = new ArrayList<>();\n"
        "        for (int i = 0; i < numCourses; i++) {\n"
        "            graph.add(new ArrayList<>());\n"
        "        }\n"
        "        int[] indegree = new int[numCourses];\n"
        "        for (int[] edge : prerequisites) {\n"
        "            graph.get(edge[1]).add(edge[0]);\n"
        "            indegree[edge[0]]++;\n"
        "        }\n"
        "        Queue<Integer> queue = new ArrayDeque<>();\n"
        "        for (int course = 0; course < numCourses; course++) {\n"
        "            if (indegree[course] == 0) {\n"
        "                queue.add(course);\n"
        "            }\n"
        "        }\n"
        "        int seen = 0;\n"
        "        while (!queue.isEmpty()) {\n"
        "            int course = queue.remove();\n"
        "            seen++;\n"
        "            for (int next : graph.get(course)) {\n"
        "                indegree[next]--;\n"
        "                if (indegree[next] == 0) {\n"
        "                    queue.add(next);\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "        return seen == numCourses;\n"
        "    }\n\n"
    )


def java_linked_list_contract_check_expressions(
    contract: Any,
    actual: str | None,
    return_type: str,
    input_vars: dict[str, str],
    list_node_snapshots: dict[str, str],
    index: int,
) -> list[str]:
    if not isinstance(contract, dict):
        return []
    lines: list[str] = []
    result = contract.get("result")
    if result is not None:
        if not isinstance(result, dict) or return_type != "ListNode" or actual is None:
            raise ValueError("linked-list result contract requires a ListNode return")
        source_name = result.get("from")
        if not isinstance(source_name, str) or source_name not in list_node_snapshots:
            raise ValueError("linked-list result contract references an unknown ListNode parameter")
        lines.append(
            "        "
            f"if (!listIdentityEquals({actual}, {list_node_snapshots[source_name]}, "
            f"{java_int_array_literal(result.get('nodeIndices'))})) "
            f"throw new AssertionError(\"case {index} linked-list result identity\");"
        )

    post_call = contract.get("postCall")
    if isinstance(post_call, dict):
        for param_name, expected_indices in post_call.items():
            if param_name not in input_vars or param_name not in list_node_snapshots:
                raise ValueError("linked-list post-call contract references an unknown ListNode parameter")
            lines.append(
                "        "
                f"if (!listIdentityEquals({input_vars[param_name]}, {list_node_snapshots[param_name]}, "
                f"{java_int_array_literal(expected_indices)})) "
                f"throw new AssertionError(\"case {index} linked-list post-call identity\");"
            )
    return lines


def java_check_expression(
    matcher: str,
    matcher_config: dict[str, Any],
    return_type: str,
    actual: str,
    expected: str,
    index: int,
    input_vars: dict[str, str],
    node_kind: str | None = None,
    forbidden_node_snapshot: str | None = None,
) -> str:
    if matcher == "exact" and return_type == "int[]":
        return f"if (!Arrays.equals({actual}, {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "int[][]":
        return f"if (!Arrays.deepEquals({actual}, {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "char[]":
        return f"if (!Arrays.equals({actual}, {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "char[][]":
        return f"if (!Arrays.deepEquals({actual}, {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "int":
        return f"if ({actual} != {expected}) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "boolean":
        return f"if ({actual} != {expected}) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "char":
        return f"if ({actual} != {expected}) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "String":
        return f"if (!Objects.equals({actual}, {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "String[]":
        return f"if (!Arrays.equals({actual}, {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type in {"List<Double>", "List<Integer>", "List<String>", "List<List<Integer>>", "List<List<String>>"}:
        return f"if (!Objects.equals({actual}, {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "unordered-list" and return_type in {"List<Integer>", "List<String>"}:
        return f"if (!unorderedFlatListEquals({actual}, {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "unordered-list-of-lists" and return_type == "int[][]":
        return f"if (!unorderedIntMatrixEquals({actual}, {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "unordered-list-of-lists" and return_type in {"List<List<Integer>>", "List<List<String>>"}:
        return f"if (!unorderedListOfListsEquals({actual}, {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "unordered-tree-list" and return_type == "List<TreeNode>":
        return f"if (!unorderedTreeListEquals({actual}, {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "float-tolerance" and return_type in {"double", "float"}:
        tolerance = java_double_literal(matcher_config.get("tolerance"))
        return f"if (!floatEquals({actual}, {expected}, {tolerance})) throw new AssertionError(\"case {index}\");"
    if matcher == "float-tolerance" and return_type in {"double[]", "List<Double>"}:
        tolerance = java_double_literal(matcher_config.get("tolerance"))
        return f"if (!floatListEquals({actual}, {expected}, {tolerance})) throw new AssertionError(\"case {index}\");"
    if matcher == "valid-topological-order" and return_type == "int[]":
        num_courses = input_vars.get("numCourses")
        prerequisites = input_vars.get("prerequisites")
        if num_courses is None or prerequisites is None:
            raise ValueError("valid-topological-order matcher requires numCourses and prerequisites parameters")
        return f"if (!validTopologicalOrder({actual}, {num_courses}, {prerequisites})) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "ListNode":
        if expected == "null":
            return f"if ({actual} != null) throw new AssertionError(\"case {index}\");"
        return f"if (!listEquals({actual}, {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "Node" and node_kind == "binary-tree-next":
        return f"if (!Objects.equals(nodeNextLevels({actual}), {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "Node" and node_kind == "graph":
        forbidden = forbidden_node_snapshot or "null"
        return f"if (!Objects.equals(graphAdjacencyValues({actual}, {forbidden}), {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "Node" and node_kind == "quad-tree":
        return f"if (!Objects.equals(quadTreeSignature({actual}), {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "Node" and node_kind == "random-list":
        forbidden = forbidden_node_snapshot or "null"
        return f"if (!Objects.equals(randomListValues({actual}, {forbidden}), {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "exact" and return_type == "TreeNode":
        return f"if (!Objects.equals(treeValues({actual}), {expected})) throw new AssertionError(\"case {index}\");"
    if matcher == "two-sum-indices" and return_type == "int[]":
        nums = input_vars.get("nums")
        target = input_vars.get("target")
        if nums is None or target is None:
            raise ValueError("two-sum-indices matcher requires nums and target parameters")
        return (
            f"if ({actual}.length != 2 || {actual}[0] == {actual}[1] || "
            f"{actual}[0] < 0 || {actual}[0] >= {nums}.length || "
            f"{actual}[1] < 0 || {actual}[1] >= {nums}.length || "
            f"{nums}[{actual}[0]] + {nums}[{actual}[1]] != {target}) "
            f"throw new AssertionError(\"case {index}\");"
        )
    if matcher == "balanced-bst-from-sorted-array" and return_type == "TreeNode":
        nums = input_vars.get("nums")
        if nums is None:
            raise ValueError("balanced-bst-from-sorted-array matcher requires nums parameter")
        return f"if (!balancedBstMatchesSortedArray({actual}, {nums})) throw new AssertionError(\"case {index}\");"
    raise ValueError(f"unsupported Java matcher/type: {matcher}/{return_type}")


def java_mutation_check_expression(
    variable: str,
    java_type: str,
    expectation: Any,
    return_actual: str | None,
    index: int,
    node_kind: str | None = None,
) -> str:
    if isinstance(expectation, dict) and ("prefix" in expectation or "lengthFrom" in expectation):
        if expectation.get("lengthFrom") != "return":
            raise ValueError("unsupported Java mutation length source")
        if return_actual is None:
            raise ValueError("prefix mutation assertions require a return value")
        actual_expression = java_copy_prefix_expression(variable, java_type, return_actual)
        expected_literal = java_literal(expectation.get("prefix"), java_type)
    else:
        actual_expression = variable
        if java_type == "Node" and node_kind == "binary-tree-next":
            return f"if (!Objects.equals(nodeNextLevels({actual_expression}), {java_int_nested_list_literal(expectation)})) throw new AssertionError(\"case {index} mutation\");"
        if java_type == "Node" and node_kind == "graph":
            return f"if (!Objects.equals(graphAdjacencyValues({actual_expression}, null), {java_int_nested_list_literal(expectation)})) throw new AssertionError(\"case {index} mutation\");"
        if java_type == "Node" and node_kind == "quad-tree":
            return f"if (!Objects.equals(quadTreeSignature({actual_expression}), {java_quad_tree_literal(expectation)})) throw new AssertionError(\"case {index} mutation\");"
        if java_type == "Node" and node_kind == "random-list":
            return f"if (!Objects.equals(randomListValues({actual_expression}, null), {java_random_list_values_literal(expectation)})) throw new AssertionError(\"case {index} mutation\");"
        if java_type == "TreeNode":
            return f"if (!Objects.equals(treeValues({actual_expression}), {java_tree_values_literal(expectation)})) throw new AssertionError(\"case {index} mutation\");"
        if java_type == "ListNode":
            if expectation is None:
                return f"if ({actual_expression} != null) throw new AssertionError(\"case {index} mutation\");"
            return f"if (!listEquals({actual_expression}, {java_int_array_literal(expectation)})) throw new AssertionError(\"case {index} mutation\");"
        expected_literal = java_literal(expectation, java_type)
    if java_type == "Node" and node_kind == "binary-tree-next":
        return f"if (!Objects.equals(nodeNextLevels({actual_expression}), {java_int_nested_list_literal(expectation)})) throw new AssertionError(\"case {index} mutation\");"
    if java_type == "Node" and node_kind == "graph":
        return f"if (!Objects.equals(graphAdjacencyValues({actual_expression}, null), {java_int_nested_list_literal(expectation)})) throw new AssertionError(\"case {index} mutation\");"
    if java_type == "Node" and node_kind == "quad-tree":
        return f"if (!Objects.equals(quadTreeSignature({actual_expression}), {java_quad_tree_literal(expectation)})) throw new AssertionError(\"case {index} mutation\");"
    if java_type == "Node" and node_kind == "random-list":
        return f"if (!Objects.equals(randomListValues({actual_expression}, null), {java_random_list_values_literal(expectation)})) throw new AssertionError(\"case {index} mutation\");"
    if java_type == "TreeNode":
        return f"if (!Objects.equals(treeValues({actual_expression}), {java_tree_values_literal(expectation)})) throw new AssertionError(\"case {index} mutation\");"
    if java_type == "ListNode":
        if expectation is None:
            return f"if ({actual_expression} != null) throw new AssertionError(\"case {index} mutation\");"
        return f"if (!listEquals({actual_expression}, {java_int_array_literal(expectation)})) throw new AssertionError(\"case {index} mutation\");"
    if java_type == "int[]":
        return f"if (!Arrays.equals({actual_expression}, {expected_literal})) throw new AssertionError(\"case {index} mutation\");"
    if java_type == "int[][]":
        return f"if (!Arrays.deepEquals({actual_expression}, {expected_literal})) throw new AssertionError(\"case {index} mutation\");"
    if java_type == "char[]":
        return f"if (!Arrays.equals({actual_expression}, {expected_literal})) throw new AssertionError(\"case {index} mutation\");"
    if java_type == "char[][]":
        return f"if (!Arrays.deepEquals({actual_expression}, {expected_literal})) throw new AssertionError(\"case {index} mutation\");"
    if java_type == "String[]":
        return f"if (!Arrays.equals({actual_expression}, {expected_literal})) throw new AssertionError(\"case {index} mutation\");"
    raise ValueError(f"unsupported Java mutation type: {java_type}")


def java_copy_prefix_expression(variable: str, java_type: str, length: str) -> str:
    if java_type in {"int[]", "int[][]", "char[]", "char[][]", "String[]"}:
        return f"Arrays.copyOf({variable}, {length})"
    raise ValueError(f"unsupported Java prefix mutation type: {java_type}")


def java_expected_literal(value: Any, java_type: str, node_kind: str | None = None) -> str:
    if java_type == "ListNode":
        if value is None:
            return "null"
        return java_literal(value, "int[]")
    if java_type == "Node" and node_kind == "binary-tree-next":
        return java_int_nested_list_literal(value)
    if java_type == "Node" and node_kind == "graph":
        return java_int_nested_list_literal(value)
    if java_type == "Node" and node_kind == "quad-tree":
        return java_quad_tree_literal(value)
    if java_type == "Node" and node_kind == "random-list":
        return java_random_list_values_literal(value)
    if java_type == "TreeNode":
        return java_tree_values_literal(value)
    return java_literal(value, java_type, node_kind=node_kind)


def is_tree_node_reference_value(value: Any) -> bool:
    return isinstance(value, dict) and set(value) == {"from", "path"} and isinstance(value.get("from"), str) and isinstance(value.get("path"), str)


def java_object_expected_literal(value: Any, java_type: str, matcher: str) -> str:
    if matcher == "object-one-of":
        if java_type == "int" and isinstance(value, dict) and set(value) == {"oneOf"}:
            return java_literal(value.get("oneOf"), "int[]")
        if java_type == "int" and type(value) is int:
            return java_literal([value], "int[]")
        raise ValueError("object-one-of matcher requires int oneOf expected values")
    return java_expected_literal(value, java_type)


def java_literal(
    value: Any,
    java_type: str,
    input_vars: dict[str, str] | None = None,
    node_kind: str | None = None,
) -> str:
    if java_type == "int":
        if not isinstance(value, int):
            raise ValueError("expected int value")
        return str(value)
    if java_type == "double":
        return java_double_literal(value)
    if java_type == "float":
        return java_float_literal(value)
    if java_type == "double[]":
        return java_double_array_literal(value)
    if java_type == "int[]":
        return java_int_array_literal(value)
    if java_type == "int[][]":
        if not isinstance(value, list) or not all(
            isinstance(row, list) and all(isinstance(item, int) for item in row)
            for row in value
        ):
            raise ValueError("expected int[][] value")
        rows = ["new int[] {" + ", ".join(str(item) for item in row) + "}" for row in value]
        return "new int[][] {" + ", ".join(rows) + "}"
    if java_type == "int[][][]":
        if not isinstance(value, list) or not all(
            isinstance(group, list)
            and all(isinstance(row, list) and all(type(item) is int for item in row) for row in group)
            for group in value
        ):
            raise ValueError("expected int[][][] value")
        groups = [java_literal(group, "int[][]") for group in value]
        return "new int[][][] {" + ", ".join(groups) + "}"
    if java_type == "char[]":
        if not isinstance(value, list) or not all(isinstance(item, str) and len(item) == 1 for item in value):
            raise ValueError("expected char[] value")
        return "new char[] {" + ", ".join(java_char_literal(item) for item in value) + "}"
    if java_type == "char[][]":
        if not isinstance(value, list) or not all(
            isinstance(row, list) and all(isinstance(item, str) and len(item) == 1 for item in row)
            for row in value
        ):
            raise ValueError("expected char[][] value")
        rows = ["new char[] {" + ", ".join(java_char_literal(item) for item in row) + "}" for row in value]
        return "new char[][] {" + ", ".join(rows) + "}"
    if java_type == "boolean":
        if not isinstance(value, bool):
            raise ValueError("expected boolean value")
        return "true" if value else "false"
    if java_type == "char":
        if not isinstance(value, str) or len(value) != 1:
            raise ValueError("expected char value")
        return java_char_literal(value)
    if java_type == "String":
        if not isinstance(value, str):
            raise ValueError("expected String value")
        return json.dumps(value)
    if java_type == "String[]":
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError("expected String[] value")
        return "new String[] {" + ", ".join(json.dumps(item) for item in value) + "}"
    if java_type == "List<Integer>":
        if not isinstance(value, list) or not all(type(item) is int for item in value):
            raise ValueError("expected List<Integer> value")
        if not value:
            return "Collections.emptyList()"
        return "Arrays.asList(" + ", ".join(str(item) for item in value) + ")"
    if java_type == "List<String>":
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError("expected List<String> value")
        if not value:
            return "Collections.emptyList()"
        return "Arrays.asList(" + ", ".join(json.dumps(item) for item in value) + ")"
    if java_type == "List<Double>":
        if not isinstance(value, list) or not all(is_finite_number(item) for item in value):
            raise ValueError("expected List<Double> value")
        if not value:
            return "Collections.emptyList()"
        return "Arrays.asList(" + ", ".join(java_double_literal(item) for item in value) + ")"
    if java_type == "List<List<Integer>>":
        if not isinstance(value, list) or not all(
            isinstance(row, list) and all(type(item) is int for item in row)
            for row in value
        ):
            raise ValueError("expected List<List<Integer>> value")
        if not value:
            return "Collections.emptyList()"
        rows = [java_literal(row, "List<Integer>") for row in value]
        return "Arrays.asList(" + ", ".join(rows) + ")"
    if java_type == "List<List<String>>":
        if not isinstance(value, list) or not all(
            isinstance(row, list) and all(isinstance(item, str) for item in row)
            for row in value
        ):
            raise ValueError("expected List<List<String>> value")
        if not value:
            return "Collections.emptyList()"
        rows = [java_literal(row, "List<String>") for row in value]
        return "Arrays.asList(" + ", ".join(rows) + ")"
    if java_type == "List<TreeNode>":
        if not isinstance(value, list):
            raise ValueError("expected List<TreeNode> value")
        if not value:
            return "Collections.emptyList()"
        trees = [java_literal(item, "TreeNode", input_vars, node_kind) for item in value]
        return "Arrays.asList(" + ", ".join(trees) + ")"
    if java_type == "ListNode":
        if value is None:
            return "null"
        if isinstance(value, dict) and set(value) == {"values", "cycleTo"}:
            values = value.get("values")
            cycle_to = value.get("cycleTo")
            if (
                not isinstance(values, list)
                or not all(type(item) is int for item in values)
                or type(cycle_to) is not int
                or cycle_to < 0
                or cycle_to >= len(values)
            ):
                raise ValueError("expected cyclic ListNode values and valid cycleTo index")
            return f"buildCyclicList({java_int_array_literal(values)}, {cycle_to})"
        return f"buildList({java_int_array_literal(value)})"
    if java_type == "ListNode[]":
        if not isinstance(value, list):
            raise ValueError("expected ListNode[] value")
        lists = [java_literal(item, "ListNode") for item in value]
        return "new ListNode[] {" + ", ".join(lists) + "}"
    if java_type == "Node" and node_kind == "binary-tree-next":
        if value is None:
            return "null"
        return f"buildNodeTree({java_integer_boxed_array_literal(value)})"
    if java_type == "Node" and node_kind == "graph":
        return f"buildGraph({java_literal(value, 'int[][]')})"
    if java_type == "Node" and node_kind == "random-list":
        return java_random_list_literal(value)
    if java_type == "TreeNode":
        if value is None:
            return "null"
        if isinstance(value, dict) and set(value) == {"from", "path"}:
            if input_vars is None or value.get("from") not in input_vars or not isinstance(value.get("path"), str):
                raise ValueError("expected TreeNode reference with available source")
            return f"treeNodeAtPath({input_vars[value['from']]}, {java_string_literal(value['path'])})"
        return f"buildTree({java_integer_boxed_array_literal(value)})"
    raise ValueError(f"unsupported Java type {java_type}")


def java_double_literal(value: Any) -> str:
    if not is_finite_number(value):
        raise ValueError("expected finite double value")
    return repr(float(value)) + "d"


def java_float_literal(value: Any) -> str:
    if not is_finite_number(value):
        raise ValueError("expected finite float value")
    return repr(float(value)) + "f"


def java_int_array_literal(value: Any) -> str:
    if not isinstance(value, list) or not all(type(item) is int for item in value):
        raise ValueError("expected int[] value")
    return "new int[] {" + ", ".join(str(item) for item in value) + "}"


def java_double_array_literal(value: Any) -> str:
    if not isinstance(value, list) or not all(is_finite_number(item) for item in value):
        raise ValueError("expected double[] value")
    return "new double[] {" + ", ".join(java_double_literal(item) for item in value) + "}"


def java_integer_boxed_array_literal(value: Any) -> str:
    if not isinstance(value, list) or not all(item is None or type(item) is int for item in value):
        raise ValueError("expected Integer[] value")
    return "new Integer[] {" + ", ".join("null" if item is None else str(item) for item in value) + "}"


def java_int_nested_list_literal(value: Any) -> str:
    if not isinstance(value, list) or not all(
        isinstance(row, list) and all(type(item) is int for item in row)
        for row in value
    ):
        raise ValueError("expected List<List<Integer>> value")
    if not value:
        return "Collections.emptyList()"
    rows = [java_literal(row, "List<Integer>") for row in value]
    return "Arrays.asList(" + ", ".join(rows) + ")"


def java_random_list_literal(value: Any) -> str:
    if not isinstance(value, list):
        raise ValueError("expected random-list Node value")
    node_values = []
    random_indices = []
    for row in value:
        if not isinstance(row, list) or len(row) != 2:
            raise ValueError("expected random-list rows")
        node_value, random_index = row
        if type(node_value) is not int:
            raise ValueError("expected random-list node value")
        if random_index is not None and (type(random_index) is not int or random_index < 0 or random_index >= len(value)):
            raise ValueError("expected random-list random index")
        node_values.append(node_value)
        random_indices.append(-1 if random_index is None else random_index)
    return f"buildRandomList({java_int_array_literal(node_values)}, {java_int_array_literal(random_indices)})"


def java_random_list_values_literal(value: Any) -> str:
    if not isinstance(value, list):
        raise ValueError("expected random-list Node values")
    if not value:
        return "Collections.emptyList()"
    rows = []
    for row in value:
        if not isinstance(row, list) or len(row) != 2:
            raise ValueError("expected random-list value rows")
        node_value, random_index = row
        if type(node_value) is not int:
            raise ValueError("expected random-list node value")
        if random_index is not None and (type(random_index) is not int or random_index < 0 or random_index >= len(value)):
            raise ValueError("expected random-list random index")
        second = "null" if random_index is None else str(random_index)
        rows.append(f"Arrays.asList({node_value}, {second})")
    return "Arrays.asList(" + ", ".join(rows) + ")"


def java_quad_tree_literal(value: Any) -> str:
    return java_string_literal(canonical_quad_tree_string(value))


def canonical_quad_tree_string(value: Any) -> str:
    if not isinstance(value, dict):
        raise ValueError("expected quad-tree object")
    required = {"val", "isLeaf", "topLeft", "topRight", "bottomLeft", "bottomRight"}
    if set(value) != required:
        raise ValueError("expected quad-tree fields")
    val = value.get("val")
    is_leaf = value.get("isLeaf")
    if type(val) is not bool or type(is_leaf) is not bool:
        raise ValueError("expected quad-tree boolean fields")
    children = [value.get("topLeft"), value.get("topRight"), value.get("bottomLeft"), value.get("bottomRight")]
    if is_leaf and any(child is not None for child in children):
        raise ValueError("expected quad-tree leaf without children")
    if not is_leaf and any(child is None for child in children):
        raise ValueError("expected quad-tree internal node with four children")
    child_literals = [
        None if child is None else json.loads(canonical_quad_tree_string(child))
        for child in children
    ]
    payload = {
        "val": val if is_leaf else True,
        "isLeaf": is_leaf,
        "topLeft": child_literals[0],
        "topRight": child_literals[1],
        "bottomLeft": child_literals[2],
        "bottomRight": child_literals[3],
    }
    return json.dumps(payload, separators=(",", ":"))


def java_tree_values_literal(value: Any) -> str:
    if value is None:
        return "Collections.emptyList()"
    if not isinstance(value, list) or not all(item is None or type(item) is int for item in value):
        raise ValueError("expected TreeNode level-order value")
    if not value:
        return "Collections.emptyList()"
    return "Arrays.asList(" + ", ".join("null" if item is None else str(item) for item in value) + ")"


def java_string_literal(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("expected String value")
    return json.dumps(value)


def java_char_literal(value: str) -> str:
    if value == "'":
        return "'\\''"
    if value == "\\":
        return "'\\\\'"
    if value == "\n":
        return "'\\n'"
    if value == "\r":
        return "'\\r'"
    if value == "\t":
        return "'\\t'"
    return "'" + value + "'"
