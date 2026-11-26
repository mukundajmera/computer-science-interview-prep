# Sliding Window Maximum

## Overview

Given an array and window size `k`, return the maximum value in every contiguous window of size `k`.

This is an advanced sliding-window problem because the maintained state is not a scalar. A monotonic deque stores candidate indices whose values decrease from front to back.

## Requirements and constraints

- Return one maximum per full window.
- `1 <= k <= n`.
- Prefer `O(n)` time.
- Use `O(k)` auxiliary space for the deque.
- Do not recompute the maximum by scanning each window.

## High-level design / approach

1. Maintain a deque of indices, not values.
2. Before adding `right`, remove back indices whose values are less than or equal to `nums[right]`; they can never be future maxima while `right` remains in range.
3. Append `right`.
4. Remove the front index if it is outside the current window.
5. Once the first full window exists, `nums[deque.front]` is the current maximum.

Invariant: deque indices are inside the current window and their values are monotonically decreasing.

## Dry run

Input: `nums = [1, 3, -1, -3, 5]`, `k = 3`.

| Right | Value | Action | Deque `index:value` | Output |
|---:|---:|---|---|---|
| 0 | 1 | append | `[0:1]` | - |
| 1 | 3 | pop `0:1`, append | `[1:3]` | - |
| 2 | -1 | append | `[1:3, 2:-1]` | 3 |
| 3 | -3 | append | `[1:3, 2:-1, 3:-3]` | 3 |
| 4 | 5 | pop smaller trailing values, expire old index as needed, append | `[4:5]` | 5 |

## Language-neutral pseudocode

```text
deque = empty indices
answer = []
for right from 0 to n - 1:
    while deque not empty and nums[deque.back] <= nums[right]:
        deque.pop_back()
    deque.push_back(right)
    if deque.front <= right - k:
        deque.pop_front()
    if right >= k - 1:
        answer.append(nums[deque.front])
return answer
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Data structure choice | Uses monotonic deque, not heap or repeated scan by default |
| Candidate elimination | Explains why smaller trailing values are removed |
| Expiry handling | Drops indices that fall out of the window |
| Complexity | Each index is pushed and popped at most once, so `O(n)` |

## Common pitfalls

1. Storing values instead of indices and losing expiry information.
2. Forgetting to remove out-of-window front entries.
3. Recomputing max in `O(k)` per window.
4. Using a heap without explaining lazy deletion trade-offs.
5. Recording output before the first full window forms.

## Follow-up questions

1. How would you return sliding window minimum?
2. When is a heap acceptable despite `O(n log k)` complexity?
3. How do you process chunked input where windows span chunk boundaries?
4. How does this map to rolling p99 metrics, where exact max is not enough?

## Variants and extensions

- Sliding window minimum.
- Constrained subsequence sum with a monotonic deque.
- Rolling maximum over event-time windows.
- Approximate percentile windows using sketches or histograms.

## Cross-links

- [Sliding Window Overview](./01-overview.md)
- [Maximum Sum Subarray of Size K](./02-maximum-sum-subarray-size-k.md)
- [HLD Stream Processing](../../03-hld-concepts/stream-processing/THEORY.md)
- [Realtime Metrics Platform HLD](../../04-hld-projects/realtime-metrics-platform/)
