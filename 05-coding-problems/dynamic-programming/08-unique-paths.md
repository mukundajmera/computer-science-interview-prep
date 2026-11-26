# Unique Paths

## Overview

Given an `m x n` grid, count how many unique paths exist from the top-left cell to the bottom-right cell if moves are only right or down.

This is grid DP. Each cell's path count comes from the cell above and the cell to the left.

## Requirements and constraints

- Start at `(0, 0)` and end at `(m - 1, n - 1)`.
- Only right and down moves are allowed.
- Return the number of paths.
- Prefer `O(m * n)` time; space can be `O(n)`.

## Recognition cue

"Count paths in a grid with restricted movement" points to DP over cells.

## State definition

`dp[r][c]` is the number of ways to reach cell `(r, c)`.

## High-level design / approach

1. First row and first column each have one path because there is only one direction to move.
2. For every other cell:
   - paths from above: `dp[r - 1][c]`;
   - paths from left: `dp[r][c - 1]`.
3. Add them: `dp[r][c] = dp[r - 1][c] + dp[r][c - 1]`.
4. Return bottom-right value.

## Dry run

`m = 3`, `n = 3`.

| Cell | Calculation | Paths |
|---|---|---:|
| `(0,0)` | start | 1 |
| first row/col | only one route | 1 |
| `(1,1)` | top `1` + left `1` | 2 |
| `(1,2)` | top `1` + left `2` | 3 |
| `(2,1)` | top `2` + left `1` | 3 |
| `(2,2)` | top `3` + left `3` | 6 |

Answer: `6`.

## Language-neutral pseudocode

```text
dp = matrix m by n
for r from 0 to m - 1:
    for c from 0 to n - 1:
        if r == 0 and c == 0:
            dp[r][c] = 1
        else:
            from_top = dp[r - 1][c] if r > 0 else 0
            from_left = dp[r][c - 1] if c > 0 else 0
            dp[r][c] = from_top + from_left
return dp[m - 1][n - 1]
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| State | Defines paths to a cell |
| Transition | Uses only top and left because moves are right/down |
| Base cases | Handles first row/column |
| Complexity | States `O(m * n)` time and `O(m * n)` or compressed `O(n)` space |
| Optimization | Explains `O(n)` row compression |

## Common pitfalls

1. Double-counting paths by allowing reverse moves.
2. Forgetting first row or first column base cases.
3. Returning `dp[m][n]` with off-by-one indexing.
4. Using DFS enumeration and timing out.

## Follow-up questions

1. What changes if obstacles are present?
2. How would you minimize path cost instead of count paths?
3. How would diagonal moves alter the recurrence?

## Variants and extensions

- Unique Paths II with obstacles.
- Minimum path sum.
- Edit-distance table movement.

## Cross-links

- [Dynamic Programming Overview](./01-overview.md)
- [Back-of-Envelope Estimation](../../00-theory/system-design-fundamentals/back-of-envelope.md)
