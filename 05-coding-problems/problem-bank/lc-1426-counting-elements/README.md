# Counting Elements

- Canonical ID: `lc-1426-counting-elements`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Count elements x in an array for which x + 1 also appears in the array.

## Driver Signature

- Java: `int countElements(int[] arr)`
- Python: `countElements(arr: List[int]) -> int`

## Key Cases and Invariants

- Duplicates count individually.
- Presence of x + 1 is all that matters, not how many times it appears.

## Solution Ladder

### Tier 1: Nested search

For each element, scan the array for x + 1.

- Time: `O(n^2)` - Each element may scan all values.
- Space: `O(1)` - Only counters are stored.

### Tier 2: Presence set

Build a set of values and count elements whose successor is present.

- Time: `O(n)` - Build and query the set in linear time.
- Space: `O(n)` - The set stores distinct values.
