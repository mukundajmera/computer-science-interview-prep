# Combination Sum II

- Canonical ID: `lc-0040-combination-sum-ii`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Find unique combinations that add to the target when each candidate position may be used at most once.

## Driver Signature

- Java: `List<List<Integer>> combinationSum2(int[] candidates, int target)`
- Python: `combinationSum2(candidates: List[int], target: int) -> List[List[int]]`

## Key Cases and Invariants

- Duplicate candidate values require duplicate-result suppression.
- Sorting enables early stop when the current value exceeds the remaining target.

## Solution Ladder

### Tier 1: Choose/skip with result set

Sort candidates, explore choose/skip decisions for every index, and let a set remove duplicate value rows.

- Time: `O(2^n * n)` - Every subset can be explored and copied into the result set.
- Space: `O(2^n * n)` - The dedupe set may hold many copied combinations plus recursion state.

### Tier 2: Sorted backtracking with duplicate skip

At each depth, iterate forward and skip equal values already considered at that same depth.

- Time: `O(2^n * n)` - The valid subset search is still exponential in the worst case, with copying cost per answer.
- Space: `O(n)` - Ignoring output, the path and recursion stack are bounded by the number of candidates.
