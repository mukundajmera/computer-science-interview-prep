# Confusing Number

- Canonical ID: `lc-1056-confusing-number`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

A number is confusing if every digit can rotate 180 degrees into another valid digit and the rotated number differs from the original.

## Driver Signature

- Java: `boolean confusingNumber(int n)`
- Python: `confusingNumber(n: int) -> bool`

## Key Cases and Invariants

- Digits 2, 3, 4, 5, and 7 make the number invalid.
- Digits 6 and 9 swap with each other.
- A valid rotation that equals the original is not confusing.

## Solution Ladder

### Tier 1: String rotation

Rotate the decimal string from right to left using a digit map.

- Time: `O(d)` - Every digit is visited once.
- Space: `O(d)` - The rotated string stores d digits.

### Tier 2: Arithmetic rotation

Build the rotated number arithmetically while stripping digits from right to left.

- Time: `O(d)` - Each decimal digit is processed once.
- Space: `O(1)` - Only numeric accumulators are stored.
