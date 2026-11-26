# Multiply Strings

- Canonical ID: `lc-0043-multiply-strings`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Multiply two non-negative integer strings and return the product as a string without converting the full inputs to built-in integer types.

## Driver Signature

- Java: `String multiply(String num1, String num2)`
- Python: `multiply(num1: str, num2: str) -> str`

## Key Cases and Invariants

- A zero operand should return exactly `0`.
- Grade-school multiplication can be represented by shifted partial products or a shared digit array.

## Solution Ladder

### Tier 1: Partial product strings

Build one shifted partial product per multiplier digit and add it into the running string result.

- Time: `O(n(m + n))` - For each multiplier digit, a partial product and string addition can touch the product length.
- Space: `O(m + n)` - The largest partial product and running result are bounded by the output digit count.

### Tier 2: Shared digit array

Accumulate each digit-pair product directly into its grade-school array positions.

- Time: `O(mn)` - Every pair of input digits contributes once.
- Space: `O(m + n)` - The result array has at most `m + n` digits.
