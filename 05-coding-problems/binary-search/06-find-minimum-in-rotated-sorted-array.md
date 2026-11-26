# Find Minimum in Rotated Sorted Array

## Overview

Given a rotated sorted array with distinct values, return the minimum value.

This is pivot discovery. Instead of looking for a target, compare `nums[mid]` with `nums[right]` to decide whether the minimum lies at or left of `mid`, or strictly right of `mid`.

## Requirements and constraints

- Array is non-empty.
- Original array was sorted ascending and rotated once.
- Values are distinct unless stated otherwise.
- Return the minimum value, not the pivot index, unless asked.
- Prefer `O(log n)` time and `O(1)` space.

## High-level design / approach

1. Initialize `left = 0`, `right = n - 1`.
2. While `left < right`, compute `mid`.
3. If `nums[mid] > nums[right]`, the minimum is strictly to the right of `mid`, so set `left = mid + 1`.
4. Otherwise `nums[mid] <= nums[right]`, so the minimum is at `mid` or left of it; set `right = mid`.
5. Return `nums[left]`.

Invariant: the minimum value is always inside `[left, right]`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Pivot reasoning | Explains why comparison to `right` reveals the unsorted side |
| Candidate retention | Keeps `mid` when it may be the minimum |
| Termination | Stops when one candidate remains |
| Duplicate awareness | Notes `nums[mid] == nums[right]` becomes ambiguous with duplicates |

## Common pitfalls

1. Setting `right = mid - 1` and discarding the actual minimum.
2. Comparing to `nums[left]` without handling already-sorted ranges carefully.
3. Returning `mid` instead of `nums[left]`.
4. Ignoring the non-empty precondition.

## Follow-up questions

1. How do duplicates change the worst-case time?
2. How would you return the rotation count?
3. How does this differ from searching for a target in a rotated array?

## Variants and extensions

- Find the first partition after a wrapped timestamp sequence.
- Detect the lowest active token after a consistent-hash ring wrap.
- Identify compaction boundary in a rotated sorted segment.

## Cross-links

- [Search in Rotated Sorted Array](./05-search-in-rotated-sorted-array.md)
- [HLD Consistent Hashing](../../03-hld-concepts/consistent-hashing/THEORY.md)
