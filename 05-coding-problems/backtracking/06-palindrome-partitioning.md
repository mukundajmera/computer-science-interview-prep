# Palindrome Partitioning

## Overview

Given a string, return every way to split it so every segment is a palindrome.

Backtracking chooses the next prefix cut. A branch is valid only if the chosen prefix is a palindrome.

## Requirements and constraints

- Use every character exactly once in order.
- Return all valid partitions.
- Validate each chosen substring as a palindrome.
- Consider precomputing palindrome checks when repeated checks dominate.

## Recognition cue

"Partition a string into all valid palindromic pieces" signals prefix-choice backtracking.

## Invariant or state definition

At state `(start, path)`, `path` contains palindrome substrings that exactly cover `s[0:start]`.

## High-level design / approach

1. Start at index `0` with an empty `path`.
2. If `start == s.length`, copy `path` into results.
3. For every `end` from `start` to `n - 1`:
   - check whether `s[start:end]` is a palindrome;
   - if not, skip it;
   - add the substring, recurse from `end + 1`, then undo.

## Dry run

String: `aab`.

| State | Prefix choice | Result |
|---|---|---|
| `start=0, []` | `a` | recurse with `start=1, [a]` |
| `start=1, [a]` | `a` | recurse with `start=2, [a, a]` |
| `start=2, [a, a]` | `b` | emit `[a, a, b]` |
| `start=0, []` | `aa` | recurse with `start=2, [aa]` |
| `start=2, [aa]` | `b` | emit `[aa, b]` |

`ab` is skipped because it is not a palindrome.

## Language-neutral pseudocode

```text
results = []
path = []

dfs(start):
    if start == s.length:
        results.add(copy(path))
        return

    for end from start to s.length - 1:
        if not is_palindrome(s, start, end):
            continue
        path.add(s[start..end])
        dfs(end + 1)
        path.remove_last()
```

## Complexity

- Without precomputation: up to `O(n * 2^n)` partitions/checking shape, with palindrome checks adding up to `O(n)` each in the worst case.
- With palindrome DP precomputation: `O(n^2)` preprocessing, then output-sensitive backtracking.
- Space: `O(n)` recursion and path beyond output, plus optional `O(n^2)` palindrome table.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| State | Uses `start` plus current partition path |
| Predicate | Checks each chosen prefix for palindrome validity |
| Base case | Emits only after covering the full string |
| Optimization | Mentions precomputed palindrome table as a follow-up |

## Common pitfalls

1. Skipping single-character palindromes.
2. Emitting a partition before the whole string is consumed.
3. Reordering substrings instead of preserving original order.
4. Rechecking the same palindrome ranges without discussing cost.

## Follow-up questions

1. How would you minimize the number of cuts?
2. How would you return only the count?
3. How would you precompute palindrome ranges?

## Variants and extensions

- Palindrome partitioning minimum cuts.
- Word break with dictionary-valid prefixes.
- Sentence generation from valid tokens.
- Log segmentation by valid rule predicates.

## Cross-links

- [Backtracking Overview](./01-overview.md)
- [Combination Sum](./04-combination-sum.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
