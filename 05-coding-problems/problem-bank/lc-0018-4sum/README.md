# 4Sum

- Canonical ID: `lc-0018-4sum`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Return every unique quadruplet of values whose sum equals the target.

## Driver Signature

- Java: `List<List<Integer>> fourSum(int[] nums, int target)`
- Python: `fourSum(nums: List[int], target: int) -> List[List[int]]`

## Key Cases and Invariants

- Quadruplets are value combinations; duplicate input values must not create duplicate rows.
- Use wide integer arithmetic in Java because four values can overflow an `int` sum.

## Solution Ladder

### Tier 1: Four loops with dedupe set

Sort values, inspect every index quadruple, and insert matching value rows into a set.

- Time: `O(n^4)` - Four nested loops enumerate all index quadruples.
- Space: `O(a)` - `a` unique answer rows are stored in the dedupe set and result list.

### Tier 2: Sorted two-pointer sweep

Sort the array, fix two positions, then move a low/high pair while skipping duplicate values.

- Time: `O(n^3)` - Two fixed loops and one linear two-pointer sweep dominate.
- Space: `O(a)` - Ignoring output, the sorted in-place array uses constant auxiliary space; answers store `a` rows.
