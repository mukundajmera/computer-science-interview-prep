# 3-Sum

## Overview

Find all unique triplets in an integer array whose sum is zero.

## Requirements and constraints

- Output must contain unique triplets only.
- Input may contain duplicates and negative values.
- Expected approach: sort once, then two-pointer scan per anchor.
- Target complexity: `O(n^2)` time, `O(1)` extra (excluding result storage).

## High-level design / approach

1. Sort array.
2. Fix an anchor index `i` from left to right.
3. For each anchor, run two-pointer search on subarray `(i+1 ... end)` for `-nums[i]`.
4. Skip duplicate anchors and duplicate side values after finding a triplet.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Dedupe correctness | Anchor and side duplicate skipping is precise |
| Reduction logic | Clearly maps problem to repeated 2-sum-sorted |
| Complexity | Defends `O(n^2)` bound after sort |
| Edge cases | Handles all-zero and no-solution inputs |

## Common pitfalls

1. Forgetting duplicate skipping, causing repeated triplets.
2. Mutating output order assumptions without clarification.
3. Incorrect pointer moves after recording a valid triplet.

## Follow-up questions

1. How does this generalize to `k`-sum?
2. How do you optimize for small value ranges?
3. Can you return lexicographically ordered triplets efficiently?

## Variants and extensions

- 3-sum closest.
- Triplets with custom target `T`.
- Count triplets only (without materializing list).

## Cross-links

- [Two Sum (Sorted)](./03-two-sum-sorted-array.md)
- [Triangle Number](./05-valid-triangle-number.md)
- [Interview Follow-ups Cheat Sheet](../../00-theory/cheat-sheets/interview-followups.md)
