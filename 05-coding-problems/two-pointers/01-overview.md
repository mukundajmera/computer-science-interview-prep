# Two Pointers Overview

## Overview

Two pointers is a pattern where two indices move through the same sequence under a clear invariant. The key skill is not syntax; it is eliminating impossible candidates without revisiting prior states.

## Requirements and constraints

- Target near-linear runtime for most scans.
- Prefer `O(1)` auxiliary space for array variants.
- Movement rules must be deterministic from each comparison.
- Input assumptions (sorted, bounded values, non-negative heights, etc.) must be explicit.

## High-level design / approach

1. Define pointer roles (`left`, `right`, `scan`, `write`, etc.).
2. State invariant regions before coding.
3. Use one comparison to decide one pointer movement.
4. Prove termination: each iteration strictly shrinks remaining search space.

## Scoring rubric

| Dimension | What interviewers look for |
|---|---|
| Invariant statement | Regions and pointer meanings are explicit |
| Correct movement | Pointer updates match elimination logic |
| Complexity defense | Linear pass and constant extra space are justified |
| Adaptability | Candidate maps template to new constraints quickly |

## Common pitfalls

1. Describing steps without stating invariant semantics.
2. Mixing sorted and unsorted assumptions.
3. Re-checking already eliminated ranges.
4. Forgetting boundary cases (length 0/1/2).

## Follow-up questions

1. When is sorting worth the `O(n log n)` cost for a two-pointer solution?
2. How do you adapt when duplicates must be removed from output?
3. Which problems require fast/slow vs opposite-end pointers?

## Variants and extensions

- Opposite ends on sorted arrays.
- Fast/slow compaction in-place.
- 3-way partitioning with three regions.
- Boundary-max variants for trapped volume computations.

## Cross-links

- [Two Pointers Pattern Pack](./README.md)
- [Two Sum (Sorted)](./03-two-sum-sorted-array.md)
- [3-Sum](./04-three-sum.md)
- [Sort Colors](./07-sort-colors.md)
- [Big-O Notation](../../00-theory/complexity-analysis/big-o-notation.md)
