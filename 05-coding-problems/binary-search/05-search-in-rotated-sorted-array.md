# Search in Rotated Sorted Array

## Overview

Given a sorted array that has been rotated at an unknown pivot, return the index of a target if it exists; otherwise return `-1`.

The array is not globally sorted, but every midpoint still reveals at least one sorted half when there are no duplicates. The skill is choosing which half can be discarded.

## Requirements and constraints

- The original array was sorted ascending and rotated once.
- Values are distinct unless the prompt explicitly allows duplicates.
- Return target index or `-1`.
- Prefer `O(log n)` time and `O(1)` space.
- State how duplicates would change the guarantee.

## High-level design / approach

1. Use inclusive search: `left = 0`, `right = n - 1`.
2. Compute `mid`.
3. If `nums[mid] == target`, return `mid`.
4. If `nums[left] <= nums[mid]`, the left half is sorted:
   - if `nums[left] <= target < nums[mid]`, move `right = mid - 1`;
   - otherwise move `left = mid + 1`.
5. Otherwise the right half is sorted:
   - if `nums[mid] < target <= nums[right]`, move `left = mid + 1`;
   - otherwise move `right = mid - 1`.
6. Return `-1` if the range empties.

Invariant: if the target exists, it is inside `[left, right]`; each step discards a half that cannot contain it based on the sorted-half range check.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Sorted-half detection | Correctly identifies which side is ordered |
| Range check | Uses inclusive/exclusive comparisons around `target` |
| Distinct-value assumption | Calls out duplicate degradation |
| Boundary movement | Discards a side only after proving target cannot be there |

## Common pitfalls

1. Assuming the left half is always sorted.
2. Using `target <= nums[mid]` after already checking equality.
3. Losing targets at `left` or `right` because of wrong inclusivity.
4. Claiming `O(log n)` with duplicates without explaining the ambiguity.

## Follow-up questions

1. What changes if duplicates are allowed?
2. How would you first find the pivot, then run ordinary binary search?
3. How would you search a rotated array for the first occurrence?

## Variants and extensions

- Ring-buffer search after logical rotation.
- Versioned sorted segments where the active start offset changes.
- Searching rotated daily partitions after retention compaction.

## Cross-links

- [Classic Binary Search](./02-classic-binary-search.md)
- [Find Minimum in Rotated Sorted Array](./06-find-minimum-in-rotated-sorted-array.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
