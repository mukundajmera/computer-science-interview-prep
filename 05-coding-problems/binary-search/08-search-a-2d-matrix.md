# Search a 2D Matrix

## Overview

Given an `m x n` matrix where each row is sorted and the first value of each row is greater than the last value of the previous row, determine whether a target exists.

The matrix is globally sorted in row-major order. Treat it as a virtual one-dimensional sorted array, then map a virtual index back to `(row, col)`.

## Requirements and constraints

- Rows are sorted ascending.
- Row boundaries preserve global order.
- Return true/false, or an index pair if the prompt asks.
- Prefer `O(log(mn))` time and `O(1)` space.
- Do not flatten the matrix into a new array.

## High-level design / approach

1. Let `rows = m`, `cols = n`, and search virtual indices `[0, rows * cols - 1]`.
2. For a virtual `mid`, compute:
   - `row = mid // cols`;
   - `col = mid % cols`.
3. Compare `matrix[row][col]` to target.
4. Move `left` or `right` exactly as in classic binary search.
5. Return false when the virtual range empties.

Invariant: if the target exists, its row-major virtual index is inside `[left, right]`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Shape recognition | Confirms row-major global sortedness, not just per-row sortedness |
| Index mapping | Converts `mid` to `(row, col)` correctly |
| Space discipline | Avoids flattening the matrix |
| Complexity | Uses `O(log(mn))` comparisons |

## Common pitfalls

1. Applying this approach when rows are sorted but row ranges overlap.
2. Flattening the matrix and paying `O(mn)` space.
3. Using `mid // rows` instead of `mid // cols`.
4. Ignoring empty matrix or empty row inputs.
5. Confusing this with the different matrix problem where rows and columns are sorted independently.

## Follow-up questions

1. What changes when each row and column is sorted, but rows are not globally ordered?
2. How would you return insertion position across row-major order?
3. How does this map to searching sorted shard pages or SSTable block indexes?
4. What if reading a row is expensive and should be minimized?

## Variants and extensions

- Search sorted pages where each page has a min/max key range.
- SSTable sparse index lookup before reading a disk block.
- Search-result shard page lookup using global rank windows.
- Kth smallest in a sorted matrix via answer-space search and count predicate.
- Median of two sorted arrays via partition binary search.

## Cross-links

- [Classic Binary Search](./02-classic-binary-search.md)
- [First Position / Lower Bound](./03-first-position-lower-bound.md)
- [HLD Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
- [Indexing Strategies](../../00-theory/database-concepts/indexing.md)
