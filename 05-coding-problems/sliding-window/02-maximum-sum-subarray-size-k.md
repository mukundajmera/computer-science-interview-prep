# Maximum Sum Subarray of Size K

## Overview

Given an array of numbers and an integer `k`, find the maximum sum of any contiguous subarray of exactly size `k`.

This is the cleanest fixed-window problem: the window length is constant, so every step adds one item and removes one item.

## Requirements and constraints

- Return the best sum over all windows of exactly `k` elements.
- `1 <= k <= n`.
- Prefer `O(n)` time.
- Use `O(1)` auxiliary space.
- Values may be negative; fixed-size sliding still works because the window length is not controlled by a sum predicate.

## High-level design / approach

1. Compute the sum of the first `k` elements.
2. Initialize `best` to that sum.
3. For each next index `right`:
   - add `nums[right]`;
   - subtract `nums[right - k]`;
   - update `best`.
4. Return `best`.

Invariant: after processing index `right >= k - 1`, `window_sum` equals the sum of `nums[right-k+1 ... right]`.

## Dry run

Input: `nums = [2, 1, 5, 1, 3, 2]`, `k = 3`.

| Window | Sum | Best |
|---|---:|---:|
| `[2, 1, 5]` | 8 | 8 |
| `[1, 5, 1]` | 7 | 8 |
| `[5, 1, 3]` | 9 | 9 |
| `[1, 3, 2]` | 6 | 9 |

## Language-neutral pseudocode

```text
window_sum = sum(nums[0:k])
best = window_sum
for right from k to n - 1:
    window_sum += nums[right]
    window_sum -= nums[right - k]
    best = max(best, window_sum)
return best
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Window invariant | Maintains exactly `k` elements |
| State update | Adds entering item and removes leaving item once |
| Edge handling | Handles `k = 1`, `k = n`, negative values |
| Complexity | `O(n)` time and `O(1)` space |

## Common pitfalls

1. Recomputing each window sum from scratch.
2. Updating `best` before the first full window exists.
3. Forgetting that all-negative arrays still have a maximum window.
4. Off-by-one removal: subtracting `nums[right-k+1]` instead of `nums[right-k]`.

## Follow-up questions

1. How would you return the start/end indices of the best window?
2. How would you compute maximum average of size `k`?
3. How would you process a stream where only the last `k` items are retained?

## Variants and extensions

- Maximum average subarray of size `k`.
- Count windows whose sum exceeds a threshold.
- Rolling error-rate or latency average over the last `k` events.

## Cross-links

- [Sliding Window Overview](./01-overview.md)
- [Sliding Window Maximum](./08-sliding-window-maximum.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
- [Realtime Metrics Platform HLD](../../04-hld-projects/realtime-metrics-platform/)
