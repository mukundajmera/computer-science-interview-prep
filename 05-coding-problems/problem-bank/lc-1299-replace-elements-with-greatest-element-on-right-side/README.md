# Replace Elements With Greatest Element On Right Side

- Canonical ID: `lc-1299-replace-elements-with-greatest-element-on-right-side`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Replace each element with the greatest value strictly to its right; the final element becomes -1.

## Driver Signature

- Java: `int[] replaceElements(int[] arr)`
- Python: `replaceElements(arr: List[int]) -> List[int]`

## Key Cases and Invariants

- The current value must not influence its own replacement.
- Scanning from the right maintains the best suffix maximum so far.

## Solution Ladder

### Tier 1: Nested scan

For every position, scan all values to its right to find the replacement.

- Time: `O(n^2)` - Each position may scan the suffix after it.
- Space: `O(n)` - A new result array is returned.

### Tier 2: Right suffix maximum

Scan from right to left, writing the best value seen so far before incorporating the current value.

- Time: `O(n)` - Each element is visited once.
- Space: `O(n)` - The returned array stores n replacements.
