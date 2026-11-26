# Coding Problem Bank

This directory contains canonical coding-problem entries. External lists such as LeetCode Top Interview 150, Grind, and NeetCode views point to these canonical IDs instead of duplicating problem or solution content.

See `IMPLEMENTATION-PLAN.md` for the end-to-end wave plan and per-problem quality gate.

## Canonical Rules

- One folder per canonical problem.
- LeetCode-backed IDs use `lc-<zero-padded-id>-<title-slug>`.
- Collection membership lives in `problem.json`.
- Completed folders must include a `cleanRoomReview` receipt in `problem.json`.
- Test cases in `cases.json` must be authored for this repository.
- Solution tiers in `solutions.json` are capped at five.
- Java and Python implementations must use the same driver signature.
- Generated driver artifacts and compiled files must stay outside this repository.

## Status Values

| Status | Meaning |
|---|---|
| `metadata-only` | External list metadata is tracked, but no repo-authored problem page exists. |
| `planned` | Generated collection status for a canonical ID with no folder yet. |
| `stub` | A canonical folder exists but solutions are not complete. |
| `solution-draft` | Java/Python solutions, cases, clean-room review, and validation receipts exist, but source-use, algorithm, driver, or collection-link review has not promoted the folder to `verified` or `reviewed`. |
| `verified` | Strict catalog validation, driver generation, and generated drivers have passed for available local toolchains, with any blocked language toolchain explicitly reported. |
| `reviewed` | Source-use, algorithm, driver, and portal review gates have passed. |

## Current Driver Surface

Generated drivers currently support scalar values, arrays, matrices, string arrays, nested lists, floating-point tolerance checks, unordered flat and nested-list matchers, in-place mutation checks, plain and cyclic singly linked lists, binary trees, custom `Node` shapes, and object-operation sequences for stateful design problems. Linked-list cases encode a chain as a JSON integer array and an empty chain as `null`; cyclic list inputs use `{ "values": [...], "cycleTo": index }`; Java signatures use `ListNode`, and Python signatures use `Optional[ListNode]`. Array/list-of-head linked-list inputs encode each slot as either `null` or a JSON integer array; Java signatures use `ListNode[]`, and Python signatures use `List[Optional[ListNode]]`. Tree cases encode a binary tree as a level-order JSON array with `null` gaps and trimmed trailing nulls; Java signatures use `TreeNode`, and Python signatures use `Optional[TreeNode]`. Custom `Node` signatures must declare `signature.customTypes.Node`; supported kinds are `binary-tree-next`, graph adjacency lists, random-pointer lists, and return-only quad trees. Unordered nested-list matching supports `List<List<Integer>>`, `List<List<String>>`, and official Java `int[][]` returns with multiset row semantics. Object-operation cases create one fresh instance per case and require each constructor or method operation to declare `input` and `expected` explicitly.

## Validation

```bash
python3 scripts/check_coding_problem_catalog.py
python3 scripts/check_coding_problem_catalog.py --driver-generation
```

Executable solution drivers are explicit checks because they run trusted local repository solution code. The current runner uses temp directories, subprocess isolation, process-session timeout cleanup, and minimal environment variables, but it is not a security sandbox for untrusted code:

```bash
python3 scripts/check_coding_problem_catalog.py --drivers --allow-unsafe-driver-execution --language python
python3 scripts/check_coding_problem_catalog.py --drivers --allow-unsafe-driver-execution --language java
```

## Scaffold Next Problem

```bash
python3 scripts/scaffold_coding_problem.py lc-0704-binary-search
```

The scaffold command creates a clean-room `stub` from source metadata only. It does not create cases or solutions.
