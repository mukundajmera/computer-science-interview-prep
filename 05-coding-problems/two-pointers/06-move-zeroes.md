# Move Zeroes

## Overview

Move all zero values to the end of the array while preserving relative order of non-zero values, in-place.

## Requirements and constraints

- Stable order for non-zero elements.
- In-place mutation only.
- Target `O(n)` time and `O(1)` extra space.

## High-level design / approach

- Keep `scan` pointer over all indices.
- Keep `write` pointer for next non-zero placement.
- On non-zero at `scan`, swap with `write` and increment `write`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Pointer roles | Clearly differentiates scan vs write semantics |
| Stability | Demonstrates order preservation |
| Complexity | One pass, constant extra memory |
| Code quality | Handles all-zero/all-non-zero gracefully |

## Common pitfalls

1. Using extra buffer despite in-place requirement.
2. Breaking stability by partition-style swaps without care.
3. Confusing `write` with first-zero semantics in explanation.

## Follow-up questions

1. Can this be done with fewer writes on flash-sensitive storage?
2. How do you generalize for moving all negatives to one side stably?
3. How would you support immutable arrays?

## Variants and extensions

- Move target value `x` to end, stable.
- Remove duplicates in sorted array (same fast/slow shape).
- Compact valid records in streaming pipelines.

## Cross-links

- [Sort Colors](./07-sort-colors.md)
- [LLD Data Modeling](../../00-theory/database-concepts/data-modeling.md)
