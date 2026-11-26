# Search In Rotated Sorted Array II

- Canonical ID: `lc-0081-search-in-rotated-sorted-array-ii`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Return whether a target exists in a sorted array that was rotated and may contain duplicate values.

## Driver Signature

- Java: `boolean search(int[] nums, int target)`
- Python: `search(nums: List[int], target: int) -> bool`

## Key Cases and Invariants

- Duplicates can hide which side is sorted; shrinking equal ends is the fallback.
- The worst case degrades to linear time when many equal values block binary-search decisions.

## Solution Ladder

### Tier 1: Linear scan

Scan each value until the target is found or the array is exhausted.

- Time: `O(n)` - Every value may be inspected once.
- Space: `O(1)` - Only the loop state is stored.

### Tier 2: Duplicate-aware binary search

Use rotated binary search when one side is known sorted, and shrink both ends when duplicates make the order ambiguous.

- Time: `O(n)` - The duplicate-shrinking fallback can remove only one value per step in the worst case; otherwise it behaves like O(log n).
- Space: `O(1)` - The search keeps only three indices.
