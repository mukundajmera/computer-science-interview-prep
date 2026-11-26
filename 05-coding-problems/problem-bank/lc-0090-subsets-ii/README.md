# Subsets II

- Canonical ID: `lc-0090-subsets-ii`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Return every unique subset of an integer list that may contain duplicate values.

## Driver Signature

- Java: `List<List<Integer>> subsetsWithDup(int[] nums)`
- Python: `subsetsWithDup(nums: List[int]) -> List[List[int]]`

## Key Cases and Invariants

- Duplicate input values must not create duplicate subset rows.
- Sorting groups equal values so duplicate branches can be skipped at each recursion depth.

## Solution Ladder

### Tier 1: Bitmask with set dedupe

Generate every index subset and store sorted value rows in a set.

- Time: `O(2^n * n)` - All masks are inspected and each row can cost linear time to copy.
- Space: `O(2^n * n)` - The dedupe set can store every unique subset.

### Tier 2: Sorted backtracking skip

Sort first, then skip equal values already considered at the same depth.

- Time: `O(a * n)` - `a` unique subsets are emitted and copied.
- Space: `O(n)` - Ignoring output, the path and recursion stack are linear.
