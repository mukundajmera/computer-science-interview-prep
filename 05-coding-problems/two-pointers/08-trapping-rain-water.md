# Trapping Rain Water

## Overview

Given bar heights, compute total trapped water after rain.

## Requirements and constraints

- Width of each bar is 1.
- Need total trapped volume.
- Prefer `O(n)` time and `O(1)` extra space.

## High-level design / approach

- Initialize `left`, `right` at ends.
- Track `leftMax`, `rightMax`.
- If `height[left] <= height[right]`, trapped water at `left` depends on `leftMax`; process left side and move `left`.
- Else process right side symmetrically.

Reasoning: smaller boundary side is the active limiter; that side can be finalized without full future knowledge of the opposite side.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Boundary logic | Correctly explains limiter-side finalization |
| State variables | Uses running maxima safely |
| Complexity | Single pass, constant extra space |
| Correctness proof | Avoids double count/negative contribution |

## Common pitfalls

1. Attempting local valley rules without global boundary logic.
2. Updating maxima in wrong order before accumulation.
3. Off-by-one in pointer advance.

## Follow-up questions

1. How does stack-based solution compare with two-pointer in trade-offs?
2. Can you return per-index trapped water profile as well?
3. How do you process chunked input with boundaries across chunks?

## Variants and extensions

- 2D rain water variant (priority queue / BFS).
- Online approximation for telemetry streams.
- Per-segment water diagnostics.

## Cross-links

- [Container With Most Water](./02-container-with-most-water.md)
- [Read Scaling](../../03-hld-concepts/read-scaling/THEORY.md)
- [Caching](../../03-hld-concepts/caching/THEORY.md)
