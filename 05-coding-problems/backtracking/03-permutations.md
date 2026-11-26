# Permutations

## Overview

Given distinct values, return every ordering of all values.

Backtracking fixes one position at a time. Each recursive frame chooses an unused value for the next position.

## Requirements and constraints

- Use every input value exactly once in each permutation.
- Return all permutations.
- For duplicate values, either sort and skip duplicates or count frequencies.
- Expected output size is `n!`.

## Recognition cue

"All orderings", "arrangements", and "use each item exactly once" strongly signal permutation backtracking.

## Invariant or state definition

At recursive depth `d`, `path` contains `d` distinct values, and every value in `path` is marked used exactly once.

## High-level design / approach

1. Track `path` and a `used` set or boolean array.
2. If `path.length == n`, copy it into results.
3. Loop over every index.
4. Skip already-used values.
5. Add the value, mark used, recurse, then undo both.

## Dry run

Input: `[1, 2, 3]`.

| Depth | Path | Legal next values |
|---|---|---|
| 0 | `[]` | `1, 2, 3` |
| 1 | `[1]` | `2, 3` |
| 2 | `[1, 2]` | `3` |
| 3 | `[1, 2, 3]` | emit |
| 2 | `[1, 3]` | `2` |
| 3 | `[1, 3, 2]` | emit |

The same process repeats for prefixes `[2]` and `[3]`.

## Language-neutral pseudocode

```text
results = []
path = []
used = set()

dfs():
    if path.length == nums.length:
        results.add(copy(path))
        return

    for i in 0..n-1:
        if i in used:
            continue
        used.add(i)
        path.add(nums[i])
        dfs()
        path.remove_last()
        used.remove(i)
```

## Complexity

- Time: `O(n * n!)` because `n!` permutations are emitted and each copy costs `O(n)`.
- Space: `O(n)` recursion, path, and used state beyond output.
- Output space: `O(n * n!)`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| State | Tracks path and used indexes |
| Base case | Emits only when path length is `n` |
| Uniqueness | Prevents reuse in one permutation |
| Restore | Removes path item and used marker |

## Common pitfalls

1. Reusing the same value twice.
2. Forgetting to unmark `used`.
3. Handling duplicate values as if they were distinct when unique output is required.
4. Understating factorial output size.

## Follow-up questions

1. How would you handle duplicate input values?
2. How would you generate the next lexicographic permutation?
3. How would you stop after the first valid permutation under extra constraints?

## Variants and extensions

- Unique permutations with duplicates.
- K-th permutation.
- Task ordering with constraints.
- Swap-based in-place permutation generation.

## Cross-links

- [Backtracking Overview](./01-overview.md)
- [Subsets](./02-subsets.md)
- [Combination Sum](./04-combination-sum.md)
