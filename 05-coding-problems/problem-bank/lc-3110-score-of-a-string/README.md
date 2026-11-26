# Score of a String

- Canonical ID: `lc-3110-score-of-a-string`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Compute the sum of absolute character-code differences between every adjacent pair in a string.

## Driver Signature

- Java: `int scoreOfString(String s)`
- Python: `scoreOfString(s: str) -> int`

## Key Cases and Invariants

- Only adjacent pairs contribute.
- A one-character string has no adjacent pair and scores zero.

## Solution Ladder

### Tier 1: Build differences

Build a list of adjacent absolute differences and sum it.

- Time: `O(n)` - There are n - 1 adjacent differences.
- Space: `O(n)` - The difference list stores n - 1 integers.

### Tier 2: Running sum

Accumulate adjacent absolute differences directly.

- Time: `O(n)` - The string is scanned once.
- Space: `O(1)` - Only the total is stored.
