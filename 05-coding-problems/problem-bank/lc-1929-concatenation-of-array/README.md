# Concatenation of Array

- Canonical ID: `lc-1929-concatenation-of-array`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Return a new array containing the input array followed by the same values again.

## Driver Signature

- Java: `int[] getConcatenation(int[] nums)`
- Python: `getConcatenation(nums: List[int]) -> List[int]`

## Key Cases and Invariants

- The output length is exactly twice the input length.
- Relative order is preserved in both halves.

## Solution Ladder

### Tier 1: Two-pass copy

Allocate a result and copy the input into each half with two loops.

- Time: `O(n)` - Every output slot is written once.
- Space: `O(n)` - The returned array has length 2n.

### Tier 2: Modulo fill

Fill each output slot from nums[i % n] in one loop.

- Time: `O(n)` - The loop writes 2n slots.
- Space: `O(n)` - The output array is required.
