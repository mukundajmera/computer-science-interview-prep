# Climbing Stairs

## Overview

Given `n` stairs, count how many distinct ways you can reach the top if each move climbs either `1` or `2` steps.

This is the entry-level DP problem because the last move fully defines the recurrence.

## Requirements and constraints

- Count distinct sequences of moves.
- Handle `n = 0`, `n = 1`, and `n = 2`.
- Prefer `O(n)` time.
- Space can be compressed to `O(1)`.

## Recognition cue

"Number of ways to reach step `n`" with fixed move sizes signals 1D counting DP.

## State definition

`dp[i]` is the number of ways to reach step `i`.

## High-level design / approach

1. Base cases:
   - `dp[0] = 1`: one way to do nothing.
   - `dp[1] = 1`: one one-step move.
2. For `i >= 2`, the last move came from `i - 1` or `i - 2`.
3. Therefore `dp[i] = dp[i - 1] + dp[i - 2]`.
4. Return `dp[n]`.

## Dry run

`n = 5`.

| Step | Calculation | Ways |
|---:|---|---:|
| 0 | base | 1 |
| 1 | base | 1 |
| 2 | `1 + 1` | 2 |
| 3 | `2 + 1` | 3 |
| 4 | `3 + 2` | 5 |
| 5 | `5 + 3` | 8 |

## Language-neutral pseudocode

```text
if n <= 1: return 1
prev2 = 1
prev1 = 1
for i from 2 to n:
    current = prev1 + prev2
    prev2 = prev1
    prev1 = current
return prev1
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| State | Defines `dp[i]` as ways to reach step `i` |
| Transition | Explains one-step and two-step last moves |
| Base cases | Handles `0` and `1` consistently |
| Space | Shows why only two previous states are needed |

## Common pitfalls

1. Treating `dp[0]` as `0` and breaking the recurrence.
2. Returning Fibonacci with the wrong offset.
3. Forgetting that order of moves matters.

## Follow-up questions

1. What changes if allowed moves are `[1, 3, 5]`?
2. What changes if some steps are blocked?
3. How would you compute answers modulo a large number?

## Variants and extensions

- Min cost climbing stairs.
- Decode ways.
- Number of ways through a service workflow with limited transitions.

## Cross-links

- [Dynamic Programming Overview](./01-overview.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
