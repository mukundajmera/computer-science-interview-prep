# Minimum Size Subarray Sum

## Overview

Given an array of positive integers and a target, find the minimum length of a contiguous subarray whose sum is at least the target.

This is a variable-size window. Positivity matters: when the sum is too small, expanding right can help; when the sum is large enough, shrinking left may improve length without missing a better answer.

## Requirements and constraints

- Return the smallest valid length, or `0` if none exists.
- Inputs are positive integers.
- Prefer `O(n)` time and `O(1)` space.
- The validity predicate is `window_sum >= target`.

## High-level design / approach

1. Initialize `left = 0`, `window_sum = 0`, and `best = infinity`.
2. Expand `right` across the array and add `nums[right]`.
3. While `window_sum >= target`:
   - record `right - left + 1` as a candidate;
   - subtract `nums[left]`;
   - move `left` forward.
4. Return `best` if found, otherwise `0`.

Invariant: before each shrink step, `[left, right]` is valid. Shrinking tests whether a shorter valid window still exists.

## Dry run

Input: `target = 7`, `nums = [2, 3, 1, 2, 4, 3]`.

| Right | Window after expand | Shrink action | Best |
|---:|---|---|---:|
| 0 | `[2]` | invalid | inf |
| 1 | `[2, 3]` | invalid | inf |
| 2 | `[2, 3, 1]` | invalid | inf |
| 3 | `[2, 3, 1, 2]` | record 4, remove 2 | 4 |
| 4 | `[3, 1, 2, 4]` | record 4, remove 3; record 3, remove 1 | 3 |
| 5 | `[2, 4, 3]` | record 3, remove 2; record 2, remove 4 | 2 |

## Language-neutral pseudocode

```text
left = 0
window_sum = 0
best = infinity
for right from 0 to n - 1:
    window_sum += nums[right]
    while window_sum >= target:
        best = min(best, right - left + 1)
        window_sum -= nums[left]
        left += 1
return 0 if best is infinity else best
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Monotonicity | Explains why positive numbers make shrink logic safe |
| Record timing | Records candidate before removing the left item |
| Correctness | Does not skip shorter windows ending at the same `right` |
| Complexity | Each pointer moves at most `n` times |

## Common pitfalls

1. Applying this template when values can be negative.
2. Recording only once per `right` instead of shrinking repeatedly.
3. Returning infinity or `n + 1` when no valid window exists.
4. Shrinking while `window_sum > target` instead of `>= target`.

## Follow-up questions

1. What changes if the array can contain negative numbers?
2. How would you return the actual subarray boundaries?
3. How do you adapt this to "minimum window with at least K events in last T seconds"?

## Variants and extensions

- Shortest subarray with sum at least K when negatives exist (deque + prefix sums).
- Minimum window with at least one event from each category.
- Time-window alerting when rolling count crosses a threshold.

## Cross-links

- [Sliding Window Overview](./01-overview.md)
- [Longest Substring With At Most K Distinct](./05-longest-substring-at-most-k-distinct.md)
- [HLD Rate Limiting](../../03-hld-concepts/rate-limiting/THEORY.md)
- [Ad Click Aggregator HLD](../../04-hld-projects/ad-click-aggregator/)
