# Spiral Matrix II

- Canonical ID: `lc-0059-spiral-matrix-ii`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Create an `n x n` matrix filled with values from `1` through `n^2` in clockwise spiral order.

## Driver Signature

- Java: `int[][] generateMatrix(int n)`
- Python: `generateMatrix(n: int) -> List[List[int]]`

## Key Cases and Invariants

- The fill starts in the top-left corner and moves right first.
- A cell should be written exactly once.

## Solution Ladder

### Tier 1: Direction walk

Walk one cell at a time, turning right when the next cell is out of bounds or already filled.

- Time: `O(n^2)` - Every matrix cell is filled once.
- Space: `O(1)` - Ignoring the output matrix, only coordinates and direction are stored.

### Tier 2: Layer boundaries

Fill the current top row, right column, bottom row, and left column, then shrink the boundaries.

- Time: `O(n^2)` - Each cell belongs to exactly one boundary segment.
- Space: `O(1)` - Only boundary pointers and the next value are stored besides the output.
