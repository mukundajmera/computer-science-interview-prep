# Valid Triangle Number

## Overview

Count index triplets that can form valid triangle side lengths.

## Requirements and constraints

- Triangle condition: for sorted `a <= b <= c`, it is enough to check `a + b > c`.
- Count all valid index triplets.
- Prefer `O(n^2)` time and `O(1)` extra space.

## High-level design / approach

- Sort ascending.
- Iterate `c` from right to left as largest side.
- Set `left = 0`, `right = c - 1`.
- If `nums[left] + nums[right] > nums[c]`, then every index in `[left, right-1]` with `right` also works; add `right - left` and decrement `right`.
- Else increment `left`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Math reduction | Correctly reduces three inequalities to one after sorting |
| Counting jump | Uses `right-left` batch counting insight |
| Complexity | Explains why nested scan remains `O(n^2)` |
| Robustness | Handles short arrays and duplicates correctly |

## Common pitfalls

1. Checking all three inequalities post-sort (unnecessary overhead).
2. Missing batch-count optimization.
3. Incorrect side index ordering.

## Follow-up questions

1. How do you list actual triplets rather than count?
2. How does behavior change with zero or negative values?
3. What if side lengths arrive as stream updates?

## Variants and extensions

- Count acute/right/obtuse triangles separately.
- Weighted counting by perimeter bands.
- Minimum perimeter valid triangle.

## Cross-links

- [3-Sum](./04-three-sum.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
