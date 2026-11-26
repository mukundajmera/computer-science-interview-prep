# Classic Binary Search

## Overview

Given a sorted array and a target, return the target index if it exists; otherwise return `-1`.

This is the entry point for binary search because the comparison is direct: if `nums[mid] < target`, every index at or left of `mid` is too small; if `nums[mid] > target`, every index at or right of `mid` is too large.

## Requirements and constraints

- Input is sorted in ascending order.
- Return any valid target index if duplicates are allowed, unless the prompt asks for first/last.
- Return `-1` when target is absent.
- Prefer `O(log n)` time and `O(1)` space.
- Avoid midpoint overflow in fixed-width integer languages.

## High-level design / approach

1. Initialize `left = 0` and `right = n - 1`.
2. While `left <= right`, compute `mid = left + (right - left) // 2`.
3. If `nums[mid] == target`, return `mid`.
4. If `nums[mid] < target`, discard the left half with `left = mid + 1`.
5. Otherwise discard the right half with `right = mid - 1`.
6. Return `-1` after the range becomes empty.

Invariant: if the target exists and has not been returned, it is inside `[left, right]`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Sortedness use | Explains why comparison discards an entire half |
| Loop guard | Uses `left <= right` for inclusive search |
| Progress | Moves past `mid` after a failed comparison |
| Return contract | Separates found index from absent target |

## Common pitfalls

1. Using `left < right` and skipping the final candidate.
2. Setting `left = mid` or `right = mid` and looping forever.
3. Returning `left` when the target is absent.
4. Forgetting the empty-array case.

## Follow-up questions

1. How would the loop change with a half-open interval?
2. How do you return the first occurrence when duplicates exist?
3. How do you search a conceptually infinite sorted stream?

## Variants and extensions

- Search in sorted logs by timestamp.
- Look up the first cache segment whose max key may contain the request.
- Binary search a local sorted index before performing an expensive remote fetch.

## Cross-links

- [Binary Search Overview](./01-overview.md)
- [First Position / Lower Bound](./03-first-position-lower-bound.md)
- [Search Insert Position](./04-search-insert-position.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
