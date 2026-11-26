# Subarrays With Exactly K Distinct Values

## Overview

Given an array, count contiguous subarrays containing exactly `k` distinct values.

The elite move is to avoid counting exact windows directly. Count subarrays with at most `k` distinct values and subtract subarrays with at most `k - 1` distinct values.

## Requirements and constraints

- Return the count of contiguous subarrays with exactly `k` distinct values.
- `k >= 1`.
- Prefer `O(n)` time.
- Use a frequency map with `O(k)` to `O(distinct)` active space depending on constraints.

## High-level design / approach

Use helper `atMost(k)`:

1. Initialize `left = 0`, frequency map, and `count = 0`.
2. Expand `right`; update frequency map.
3. While distinct values exceed `k`, shrink from the left.
4. Every subarray ending at `right` and starting from `left` through `right` is valid, so add `right - left + 1` to `count`.

Then:

```text
exactlyK = atMost(k) - atMost(k - 1)
```

Invariant: after shrink, every start index in `[left, right]` produces a subarray ending at `right` with at most `k` distinct values.

## Dry run

Input: `nums = [1, 2, 1, 2, 3]`, `k = 2`.

For `atMost(2)`:

| Right | Value | Repaired window | Contribution |
|---:|---:|---|---:|
| 0 | 1 | `[1]` | 1 |
| 1 | 2 | `[1, 2]` | 2 |
| 2 | 1 | `[1, 2, 1]` | 3 |
| 3 | 2 | `[1, 2, 1, 2]` | 4 |
| 4 | 3 | `[2, 3]` | 2 |

`atMost(2) = 12`, `atMost(1) = 5`, so `exactly(2) = 7`.

## Language-neutral pseudocode

```text
function atMost(k):
    if k < 0: return 0
    left = 0
    freq = {}
    count = 0
    for right from 0 to n - 1:
        freq[nums[right]] += 1
        while size(freq) > k:
            freq[nums[left]] -= 1
            if freq[nums[left]] == 0: delete freq[nums[left]]
            left += 1
        count += right - left + 1
    return count

return atMost(k) - atMost(k - 1)
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Counting insight | Uses `atMost(k) - atMost(k - 1)` |
| Combinatorics | Explains why `right - left + 1` windows end at `right` |
| State maintenance | Correctly updates distinct count on add/remove |
| Complexity | Two linear passes, still `O(n)` |

## Common pitfalls

1. Trying to enumerate every exact-K subarray.
2. Adding only one count per right boundary.
3. Forgetting that `atMost(0)` should return zero.
4. Reusing a frequency map across the two helper calls.

## Follow-up questions

1. How would you count subarrays with exactly K odd numbers?
2. How do you return one example window instead of a count?
3. How would you adapt for streaming where old events expire by timestamp?

## Variants and extensions

- Count subarrays with at most K distinct.
- Count substrings containing all three required characters.
- Product analytics: sessions with exactly K event types in a recent window.

## Cross-links

- [Sliding Window Overview](./01-overview.md)
- [Longest Substring With At Most K Distinct](./05-longest-substring-at-most-k-distinct.md)
- [HLD Stream Processing](../../03-hld-concepts/stream-processing/THEORY.md)
- [Ad Click Aggregator HLD](../../04-hld-projects/ad-click-aggregator/)
