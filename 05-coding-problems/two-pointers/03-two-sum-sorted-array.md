# Two Sum (Sorted Array)

## Overview

Given a sorted integer array and a target, determine whether any pair sums to target.

## Requirements and constraints

- Input is sorted ascending.
- Return boolean pair existence for baseline version.
- Aim for `O(n)` time and `O(1)` space.

## High-level design / approach

- Initialize `left = 0`, `right = n - 1`.
- If `nums[left] + nums[right]` is too small, increment `left`.
- If too large, decrement `right`.
- Stop when sum matches target or pointers cross.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Elimination logic | Uses sorted order to justify pointer movement |
| Termination | Proves one-way progress and finite steps |
| Complexity | Explains linear bound clearly |
| Variants | Can return indices and count pairs with small changes |

## Common pitfalls

1. Applying approach to unsorted input without sorting discussion.
2. Moving both pointers on mismatch.
3. Returning wrong index convention in follow-up variants.

## Follow-up questions

1. How do you return 1-based indices instead of boolean?
2. How do you count unique pairs equal to target?
3. How does approach compare with hash-map on unsorted arrays?

## Variants and extensions

- Return one pair indices.
- Return all unique pairs.
- Closest pair sum to target.

## Cross-links

- [Two Pointers Pattern Pack](./README.md)
- [3-Sum](./04-three-sum.md)
- [Complexity Reference](../../00-theory/cheat-sheets/complexity-reference.md)
