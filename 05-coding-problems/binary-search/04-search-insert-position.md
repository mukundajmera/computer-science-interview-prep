# Search Insert Position

## Overview

Given a sorted array and a target, return the index where the target is found or where it should be inserted to preserve sorted order.

This is lower bound with a user-facing API contract. The result can be any index from `0` to `n`, including `n` when the target belongs after all existing values.

## Requirements and constraints

- Input is sorted in ascending order.
- Return the first index `i` where `nums[i] >= target`.
- Return `n` if every value is smaller than target.
- Prefer `O(log n)` time and `O(1)` space.
- Do not mutate the input.

## High-level design / approach

1. Use `left = 0`, `right = n`.
2. While `left < right`, compute `mid`.
3. If `nums[mid] >= target`, set `right = mid`.
4. Otherwise set `left = mid + 1`.
5. Return `left`.

Invariant: indices before `left` are confirmed insertion positions too far left because their values are less than target. The final `left` is the earliest legal insertion point.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Contract clarity | Returns insertion index, not only found/not found |
| Boundary completeness | Handles insertion before first and after last |
| Duplicate semantics | Inserts before existing equal values unless told otherwise |
| API reasoning | Explains why returning `n` is valid |

## Common pitfalls

1. Returning `-1` when the target is absent.
2. Forgetting `right = n` for the after-last insertion case.
3. Returning after equality when the first equal position is required.
4. Treating insertion position as a mutation operation.

## Follow-up questions

1. How would you insert after the last duplicate instead?
2. How would you support a custom comparator?
3. How does this relate to keyset pagination and index seeks?

## Variants and extensions

- Insert into a sorted in-memory leaderboard segment.
- Find the page boundary for a cursor in a sorted result list.
- Locate the first SLA threshold bucket that a latency value enters.

## Cross-links

- [First Position / Lower Bound](./03-first-position-lower-bound.md)
- [HLD API Design](../../03-hld-concepts/api-design/THEORY.md)
- [Indexing Strategies](../../00-theory/database-concepts/indexing.md)
