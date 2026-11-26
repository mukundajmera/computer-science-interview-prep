# Subsets

## Overview

Given a list of distinct values, return every possible subset.

This is the purest include/exclude backtracking problem: for each index, either skip the item or include it.

## Requirements and constraints

- Return all subsets, including the empty subset and the full set.
- Preserve input order inside each subset unless the prompt says otherwise.
- For distinct values, expected output size is `2^n`.
- If duplicates are allowed, add duplicate handling explicitly.

## Recognition cue

"All subsets", "power set", and "choose or skip each item" strongly signal include/exclude backtracking.

## Invariant or state definition

At recursive state `(index, path)`, `path` contains a valid subset formed only from elements before `index`.

## High-level design / approach

1. Start with `index = 0` and an empty `path`.
2. If `index == n`, copy `path` into results.
3. Recurse without the current item.
4. Add the current item, recurse with it, then remove it.
5. Return all copied results.

## Dry run

Input: `[1, 2]`.

| State | Choice | Result |
|---|---|---|
| `i=0, []` | skip `1` | move to `i=1, []` |
| `i=1, []` | skip `2` | emit `[]` |
| `i=1, []` | take `2` | emit `[2]` |
| `i=0, []` | take `1` | move to `i=1, [1]` |
| `i=1, [1]` | skip `2` | emit `[1]` |
| `i=1, [1]` | take `2` | emit `[1, 2]` |

## Language-neutral pseudocode

```text
results = []
path = []

dfs(index):
    if index == n:
        results.add(copy(path))
        return

    dfs(index + 1)

    path.add(nums[index])
    dfs(index + 1)
    path.remove_last()
```

## Complexity

- Time: `O(n * 2^n)` because there are `2^n` subsets and copying can cost up to `O(n)`.
- Space: `O(n)` recursion and path space beyond output.
- Output space: `O(n * 2^n)` in the worst case.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| State | Uses index plus current path |
| Base case | Emits when every item has been considered |
| Copying | Copies path before storing it |
| Complexity | Includes output copying cost |

## Common pitfalls

1. Forgetting the empty subset.
2. Adding `path` by reference instead of by copy.
3. Removing the wrong element during undo.
4. Assuming subsets must be sorted when input order is already fixed.

## Follow-up questions

1. How would you handle duplicate input values?
2. How would you generate subsets iteratively?
3. How would you return only subsets of size `k`?

## Variants and extensions

- Subsets with duplicates.
- Combinations of size `k`.
- Bitmask subset generation.
- Feature-flag rollout combinations.

## Cross-links

- [Backtracking Overview](./01-overview.md)
- [Combination Sum](./04-combination-sum.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
