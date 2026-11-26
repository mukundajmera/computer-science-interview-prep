# Binary Search Overview

## Overview

Binary search is a loop around a contract: the answer is still inside the active range, and the midpoint decision removes a range that cannot contain it. Most interview bugs happen when candidates memorize a loop but cannot say what `left`, `right`, and `mid` mean.

The safest way to learn it is to choose one interval convention, state the invariant, and map the return value to the problem contract before coding.

## Requirements and constraints

- The search space must be ordered by index, value, answer size, or predicate result.
- Each midpoint decision must discard at least one candidate.
- Boundary updates must preserve the invariant.
- The loop must terminate for one-element and two-element ranges.
- The return value must match the prompt: found index, `-1`, insertion position, first true, or optimized value.

## High-level design / approach

1. Define the candidate space: indices, values, speeds, capacities, partition sizes, or answer values.
2. Define the predicate or comparison:
   - exact search: compare `nums[mid]` with `target`;
   - lower bound: ask whether `nums[mid] >= target`;
   - answer-space search: ask whether this candidate is feasible;
   - partition search: ask whether left partitions are valid.
3. Choose interval convention:
   - inclusive `[left, right]` for exact search;
   - half-open `[left, right)` for lower-bound style;
   - inclusive value range for answer-space minimization.
4. Move only the boundary justified by the invariant.
5. Return the contract value, then separately handle not-found or impossible cases.

## Template selection

| Problem signal | Template |
|---|---|
| target exists or not in sorted array | exact search |
| first index where condition holds | lower-bound / first-true search |
| insertion position | lower-bound return `left` |
| sorted array rotated once | identify sorted half or pivot relation |
| minimum feasible speed/capacity/rate | binary search on answer |
| 2D row-major sorted matrix | map virtual 1D index to row/column |
| median/kth across sorted arrays | partition binary search as an elite follow-up |
| sparse or unknown-size source | exponential range expansion + binary search |

## Scoring rubric

| Dimension | What interviewers look for |
|---|---|
| Invariant statement | What range still may contain the answer |
| Predicate proof | Why the predicate or comparison is monotonic |
| Boundary correctness | No infinite loop, skipped candidate, or off-by-one return |
| Edge-case coverage | Empty, singleton, two elements, duplicates, all false/all true |
| Complexity defense | `O(log n)` search iterations plus feasibility-check cost |

## Common pitfalls

1. Mixing `[left, right]` and `[left, right)` rules in the same solution.
2. Updating `right = mid - 1` in a first-true search where `mid` may be the answer.
3. Returning `-1` for an insertion-position problem.
4. Assuming duplicates are harmless in rotated-array search.
5. Forgetting answer-space complexity is `O(log range * check_cost)`, not always `O(log n)`.
6. Calling any midpoint-based loop binary search even when the predicate is not monotonic.

## Follow-up questions

1. What invariant does your `left` pointer represent when the loop ends?
2. How would you adapt exact search to return the first duplicate?
3. What changes when the search space is values, not indices?
4. How do you prove feasibility is monotonic in answer-space search?
5. Why is median of two sorted arrays a partition problem rather than a direct target search?

## Variants and extensions

- Database index seek and page-boundary lookup.
- Cursor pagination using stable sort keys.
- Capacity planning via smallest feasible throughput.
- Alert threshold tuning over monotonic validation results.
- Consistent-hash ring lookup with first node clockwise from a hash.

## Cross-links

- [Binary Search Pattern Pack](./README.md)
- [Classic Binary Search](./02-classic-binary-search.md)
- [First Position / Lower Bound](./03-first-position-lower-bound.md)
- [Koko Eating Bananas](./07-koko-eating-bananas.md)
- [Search a 2D Matrix](./08-search-a-2d-matrix.md)
- [HLD Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
