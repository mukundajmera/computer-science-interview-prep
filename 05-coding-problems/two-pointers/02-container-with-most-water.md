# Container With Most Water

## Overview

Given non-negative bar heights, choose two bars that maximize contained area. Area is width times the shorter boundary height.

## Requirements and constraints

- Return maximum area from one pair.
- `n >= 2`.
- Prefer `O(n)` time and `O(1)` space.
- Width shrinks as pointers converge.

## High-level design / approach

- Start with widest pair at both ends.
- Compute area using `min(height[left], height[right]) * (right - left)`.
- Move the pointer at the shorter bar inward because moving the taller bar cannot improve the limiting height while width decreases.
- Keep best area seen.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Core insight | Correctly explains why shorter side moves |
| Correctness | Never misses best pair during elimination |
| Complexity | `O(n)` scan, `O(1)` extra space |
| Edge handling | Works for flat, strictly increasing, and decreasing inputs |

## Common pitfalls

1. Moving the taller side first.
2. Using max height instead of min height in area formula.
3. Off-by-one width calculations.

## Follow-up questions

1. How would you return the best pair indices, not just area?
2. How do ties get resolved if multiple pairs have same max area?
3. What changes if bar widths are variable?

## Variants and extensions

- Return all max-area pairs.
- Add lower/upper index constraints.
- Streamed input approximation with bounded memory.

## Cross-links

- [Two Pointers Pattern Pack](./README.md)
- [Trapping Rain Water](./08-trapping-rain-water.md)
- [Read Scaling](../../03-hld-concepts/read-scaling/THEORY.md)
