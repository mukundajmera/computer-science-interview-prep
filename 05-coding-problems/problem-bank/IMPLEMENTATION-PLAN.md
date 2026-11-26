# Coding Problem Bank Implementation Plan

## Chosen Path

Build one canonical problem folder per LeetCode-aligned problem and let source-list collections reference that folder. This avoids duplicated code when a problem appears in LeetCode Top Interview 150, Grind, and NeetCode.

## Scope Snapshot

| Source | Entries | Role |
|---|---:|---|
| LeetCode Top Interview 150 | 150 | Interview baseline |
| Grind 169 | 169 | Time-boxed practice list |
| NeetCode All | 972 | Broad backlog |
| Deduped canonical problems | 1004 | Single source of repo-authored problem details and solutions |

## Canonical Folder Contract

Each completed folder under `05-coding-problems/problem-bank/<canonical-id>/` contains:

- `problem.json` with source metadata, collection memberships, difficulty, patterns, and exact Java/Python driver signatures.
- `problem.json` clean-room review receipt covering `problem.json`, `README.md`, `cases.json`, and `solutions.json`.
- `cases.json` with repo-authored test cases only.
- `solutions.json` with one to five solution tiers, ordered from brute force to best known practical approach.
- `README.md` with repo-authored prompt summary, signatures, solution explanations, complexity analysis, pitfalls, and follow-ups.
- `java/solution-<tier>-<slug>/Solution.java`.
- `python/solution-<tier>-<slug>/solution.py`.

No folder may copy external statements, examples, constraints, editorials, or source code.

## Wave Strategy

1. Foundation wave: keep validators, source manifests, generated collection pages, and driver execution green.
2. Primitive-driver pilot wave: finish representative arrays, strings, stacks, greedy, dynamic programming, and sliding-window problems that fit the current generated driver contract.
3. Adapter wave: add explicit serializers, signatures, and matchers for linked lists, trees, matrices, nested arrays/lists, mutation-style problems, and class-design operation sequences.
4. LeetCode Top 150 wave: complete the full 150 first because it is the smallest high-value complete set.
5. Grind delta wave: add Grind problems not already covered by Top 150.
6. NeetCode backlog wave: add remaining NeetCode All problems by pattern group and difficulty.
7. Final audit wave: run source-use review, driver validation, generated coverage freshness, link checks, and full script tests.

## Per-Problem Quality Gate

For each canonical problem:

1. Run `python3 scripts/scaffold_coding_problem.py <canonical-id>` when the folder does not exist.
2. Author clean-room problem summary and test cases.
3. Define the Java and Python function signatures before writing solutions.
4. Add up to five solution tiers, stopping when the practical best approach is covered.
5. Implement Java and Python for every tier with matching behavior.
6. Add or refresh the clean-room review receipt.
7. Run generated Python driver.
8. Run generated Java driver when a JDK is available; otherwise run Java driver source generation and record the JDK blocker.
9. Mark `verified` only after generated drivers pass for available local toolchains and any blocked language toolchain is explicitly reported.
10. Mark `reviewed` only after source-use, algorithm, driver, and collection-link review.

## Validation Commands

```bash
python3 -B scripts/check_coding_problem_catalog.py --strict
python3 -B scripts/check_coding_problem_catalog.py --driver-generation
python3 -B scripts/check_coding_problem_catalog.py --drivers --allow-unsafe-driver-execution --language python
python3 -B scripts/check_coding_problem_catalog.py --drivers --allow-unsafe-driver-execution --language java
python3 -B -m unittest discover scripts/tests -v
```

If the Java runtime is unavailable, Java runtime execution is blocked; keep Java driver source generation passing and report the blocker before treating a problem as `verified`. Driver execution is for trusted local repo code only; use an OS/container sandbox before running submitted or forked code.

## Review Model

Use one implementation worker per non-overlapping problem or pattern slice. After each slice:

- Spec review: signatures, max five tiers, collection memberships, and metadata-only source contract.
- Code review: correctness, edge cases, complexity claims, and language parity.
- Risk review: path safety, generated artifacts, source-use contamination, and test isolation.

Do not batch unrelated bug fixes with new problem content.
