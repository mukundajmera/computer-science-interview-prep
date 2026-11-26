# Sort Colors

## Overview

Sort an array containing only `0`, `1`, `2` in-place without library sort.

## Requirements and constraints

- Single-pass preferred.
- Constant extra memory.
- Maintain clear region invariants for correctness.

## High-level design / approach

Use Dutch National Flag partitioning:
- `left`: next slot for `0`.
- `i`: current scan index.
- `right`: next slot for `2` from end.

Rules:
- If `nums[i] == 0`: swap `i` and `left`, then `left++`, `i++`.
- If `nums[i] == 1`: `i++`.
- If `nums[i] == 2`: swap `i` and `right`, then `right--` (do not increment `i` yet).

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Invariants | Correctly defines three/four partitions |
| Update logic | Explains why `i` may stay after right swap |
| Complexity | `O(n)` time, `O(1)` space |
| Edge handling | Handles all-2s, all-0s, and mixed runs |

## Common pitfalls

1. Incrementing `i` immediately after swapping with `right`.
2. Not describing invariant regions before coding.
3. Using counting sort despite one-pass intent.

## Follow-up questions

1. How do you extend to `k` colors?
2. What changes for stable sorting requirement?
3. How would you parallelize partitioning for large arrays?

## Variants and extensions

- Multi-pivot partitioning.
- Partition by predicate ranges.
- Streaming triage pipelines.

## Cross-links

- [Move Zeroes](./06-move-zeroes.md)
- [Strategy Pattern](../../01-design-patterns/behavioral/strategy/)
