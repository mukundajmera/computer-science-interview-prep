# Permutations II

- Canonical ID: `lc-0047-permutations-ii`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Return all unique permutations of a list that may contain duplicate values.

## Driver Signature

- Java: `List<List<Integer>> permuteUnique(int[] nums)`
- Python: `permuteUnique(nums: List[int]) -> List[List[int]]`

## Key Cases and Invariants

- Rows with the same values in the same order should appear only once.
- Sorting plus a used-array skip condition prevents duplicate branches before they are generated.

## Solution Ladder

### Tier 1: Swap permutations with set

Generate every index permutation by swapping and store value rows in a set to collapse duplicates.

- Time: `O(n! * n)` - All index permutations may be generated and each copied row costs linear time.
- Space: `O(n! * n)` - The dedupe set may store every unique row plus recursion stack.

### Tier 2: Sorted used-array backtracking

Sort values and skip a duplicate value when its previous equal value has not been used in the current branch.

- Time: `O(a * n)` - `a` unique permutations are emitted and each row costs `n` to copy.
- Space: `O(n)` - Ignoring output, only the path, used flags, and recursion stack are stored.
