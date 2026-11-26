# Longest Increasing Subsequence

## Overview

Given an array, return the length of the longest strictly increasing subsequence. Elements do not need to be contiguous, but their original order must be preserved.

This page teaches the classic `O(n^2)` DP first because it makes the state and transition clear. The `O(n log n)` patience-sorting method is an important follow-up, but it is not the first recurrence to explain.

## Requirements and constraints

- Strictly increasing means `nums[j] < nums[i]`.
- Subsequence preserves order but may skip elements.
- Return length, not necessarily the sequence.
- Baseline DP is `O(n^2)` time and `O(n)` space.

## Recognition cue

"Longest subsequence with ordered constraint" often signals DP over endings.

## State definition

`dp[i]` is the length of the longest increasing subsequence that ends exactly at index `i`.

## High-level design / approach

1. Initialize every `dp[i] = 1`, because each element alone is a subsequence.
2. For each `i`, inspect all earlier `j < i`.
3. If `nums[j] < nums[i]`, `nums[i]` can extend a subsequence ending at `j`.
4. Set `dp[i] = max(dp[i], dp[j] + 1)`.
5. Return `max(dp)`.

## Dry run

`nums = [10, 9, 2, 5, 3, 7]`.

| `i` | Value | Useful previous values | `dp[i]` |
|---:|---:|---|---:|
| 0 | 10 | none | 1 |
| 1 | 9 | none | 1 |
| 2 | 2 | none | 1 |
| 3 | 5 | `2` | 2 |
| 4 | 3 | `2` | 2 |
| 5 | 7 | `2,5,3` | 3 |

Answer so far: `3`.

## Language-neutral pseudocode

```text
if nums is empty: return 0
dp = array length n filled with 1
for i from 0 to n - 1:
    for j from 0 to i - 1:
        if nums[j] < nums[i]:
            dp[i] = max(dp[i], dp[j] + 1)
return max(dp)
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| State | Says subsequence must end at `i` |
| Transition | Extends only from smaller previous values |
| Subsequence clarity | Does not require contiguity |
| Complexity | States `O(n^2)` time and `O(n)` space for baseline DP |
| Follow-up | Knows `O(n log n)` tails method exists |

## Common pitfalls

1. Confusing subsequence with subarray.
2. Defining `dp[i]` as "best anywhere up to i" and losing transition clarity.
3. Allowing `<=` for strictly increasing.
4. Returning `dp[n - 1]` instead of `max(dp)`.

## Follow-up questions

1. How does the `O(n log n)` tails method work?
2. How would you reconstruct one LIS?
3. What changes for non-decreasing subsequence?

## Variants and extensions

- Russian Doll Envelopes.
- Longest chain of pairs.
- Ranking sequences with monotonic constraints.

## Cross-links

- [Dynamic Programming Overview](./01-overview.md)
- [Binary Search Pattern Pack](../binary-search/README.md)
