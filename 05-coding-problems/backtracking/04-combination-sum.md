# Combination Sum

## Overview

Given positive candidate numbers and a target, return all unique combinations whose sum equals the target. A candidate may usually be reused unless the prompt says otherwise.

This is backtracking over a sorted or fixed candidate list with a remaining target.

## Requirements and constraints

- Return combinations, not permutations; `[2, 3]` and `[3, 2]` are the same combination.
- Clarify whether candidates may be reused.
- Candidates are positive in the standard version, which makes `remaining < 0` a safe prune.
- If duplicate candidates exist, skip duplicate branches deliberately.

## Recognition cue

"All combinations that sum to target" signals backtracking with `start` index and `remaining` target.

## Invariant or state definition

At state `(start, remaining, path)`, `path` is nondecreasing by candidate position and sums to `target - remaining`.

## High-level design / approach

1. Sort candidates if duplicate handling or early stopping is needed.
2. Start DFS with `start = 0`, `remaining = target`.
3. If `remaining == 0`, copy `path`.
4. For each candidate index from `start` onward:
   - skip duplicates at the same recursion depth;
   - stop if candidate is greater than `remaining` after sorting;
   - add candidate and recurse.
5. Reuse the same index for unlimited reuse; use `i + 1` for single-use variants.
6. Undo the path append.

## Dry run

Candidates: `[2, 3, 6, 7]`, target `7`.

| State | Choice | Next state |
|---|---|---|
| `remaining=7, path=[]` | choose `2` | `remaining=5, path=[2]` |
| `remaining=5, path=[2]` | choose `2` | `remaining=3, path=[2,2]` |
| `remaining=3, path=[2,2]` | choose `3` | `remaining=0, path=[2,2,3]`, emit |
| `remaining=7, path=[]` | choose `7` | `remaining=0, path=[7]`, emit |

Answer: `[[2,2,3], [7]]`.

## Language-neutral pseudocode

```text
sort candidates
results = []
path = []

dfs(start, remaining):
    if remaining == 0:
        results.add(copy(path))
        return

    for i from start to candidates.length - 1:
        if i > start and candidates[i] == candidates[i - 1]:
            continue
        if candidates[i] > remaining:
            break
        path.add(candidates[i])
        dfs(i, remaining - candidates[i])   // reuse allowed
        path.remove_last()
```

## Complexity

- Time: exponential in the target and candidate count; a common loose bound is `O(branches^depth)`.
- Depth: at most `target / min_candidate` when all candidates are positive.
- Space: recursion depth plus path, excluding output.
- Output can be large and should be included separately when materializing all combinations.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| State | Uses `start`, `remaining`, and `path` |
| Combination order | Avoids generating permutations of the same combination |
| Reuse rule | Uses `i` for reuse or `i + 1` for single-use |
| Pruning | Stops when sorted candidate exceeds remaining target |

## Common pitfalls

1. Reordering combinations and producing duplicates.
2. Using `i + 1` when reuse is allowed.
3. Using `i` when candidates can be used once.
4. Pruning on `remaining < 0` when candidates may be negative.

## Follow-up questions

1. How does the solution change for Combination Sum II?
2. How would you return only the count?
3. What if candidates include zero or negative numbers?

## Variants and extensions

- Combination Sum II with single-use candidates.
- Coin change combinations.
- Bounded inventory fulfillment.
- Menu bundle selection under a budget.

## Cross-links

- [Backtracking Overview](./01-overview.md)
- [Subsets](./02-subsets.md)
- [Palindrome Partitioning](./06-palindrome-partitioning.md)
