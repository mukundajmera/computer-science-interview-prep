# House Robber

## Overview

Given a line of houses with money values, compute the maximum money that can be robbed without robbing adjacent houses.

This is 1D optimization DP with a choose-or-skip decision at each index.

## Requirements and constraints

- Houses are arranged in a line.
- Cannot choose adjacent houses.
- Return maximum total value.
- Prefer `O(n)` time and `O(1)` compressed space.

## Recognition cue

"Maximize value but cannot take adjacent items" signals DP because a local largest house may block a better combination later.

## State definition

`dp[i]` is the best total using houses from `0` through `i`.

## High-level design / approach

For each house `i`, choose between:

1. Skip house `i`: keep `dp[i - 1]`.
2. Rob house `i`: take `nums[i] + dp[i - 2]`.

So `dp[i] = max(dp[i - 1], nums[i] + dp[i - 2])`.

## Dry run

`nums = [2, 7, 9, 3, 1]`.

| `i` | Value | Skip | Take | Best |
|---:|---:|---:|---:|---:|
| 0 | 2 | 0 | 2 | 2 |
| 1 | 7 | 2 | 7 | 7 |
| 2 | 9 | 7 | 11 | 11 |
| 3 | 3 | 11 | 10 | 11 |
| 4 | 1 | 11 | 12 | 12 |

Answer: `12`.

## Language-neutral pseudocode

```text
prev2 = 0
prev1 = 0
for value in nums:
    current = max(prev1, prev2 + value)
    prev2 = prev1
    prev1 = current
return prev1
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Choice model | Names skip vs take |
| Dependency | Uses `i - 1` and `i - 2` only |
| Edge cases | Empty and one-house arrays work |
| Complexity | `O(n)` time, `O(1)` space after compression |

## Common pitfalls

1. Greedily picking the larger of every adjacent pair.
2. Using `dp[i - 1] + nums[i]`, which violates adjacency.
3. Forgetting empty input.
4. Compressing variables in the wrong order.

## Follow-up questions

1. What changes if houses are circular?
2. How would you return which houses were robbed?
3. How would negative values affect the recurrence?

## Variants and extensions

- Delete and Earn.
- Maximum sum of non-adjacent nodes in a tree.
- Scheduling non-overlapping jobs.

## Cross-links

- [Dynamic Programming Overview](./01-overview.md)
- [Job Scheduler HLD](../../04-hld-projects/job-scheduler/)
