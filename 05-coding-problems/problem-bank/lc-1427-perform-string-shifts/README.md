# Perform String Shifts

- Canonical ID: `lc-1427-perform-string-shifts`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Apply left and right cyclic string shifts and return the final string.

## Driver Signature

- Java: `String stringShift(String s, int[][] shift)`
- Python: `stringShift(s: str, shift: List[List[int]]) -> str`

## Key Cases and Invariants

- Only the net shift matters.
- Left shifts and right shifts cancel each other modulo string length.

## Solution Ladder

### Tier 1: Simulate each shift

Apply every shift by slicing the current string.

- Time: `O(qn)` - Each of q shifts can copy n chars.
- Space: `O(n)` - Slicing creates new strings.

### Tier 2: Net shift

Combine all shifts into one right rotation modulo n.

- Time: `O(q + n)` - Compute net shift then slice once.
- Space: `O(n)` - The returned string is a new string.
