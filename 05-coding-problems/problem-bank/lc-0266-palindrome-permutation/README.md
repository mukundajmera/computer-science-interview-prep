# Palindrome Permutation

- Canonical ID: `lc-0266-palindrome-permutation`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Determine whether the characters of a string can be rearranged to form a palindrome.

## Driver Signature

- Java: `boolean canPermutePalindrome(String s)`
- Python: `canPermutePalindrome(s: str) -> bool`

## Key Cases and Invariants

- At most one character may have an odd count.
- Parity tracking is enough; exact counts are not required.

## Solution Ladder

### Tier 1: Frequency count

Count every character and then count odd frequencies.

- Time: `O(n)` - The string is scanned and the count map is scanned.
- Space: `O(u)` - The map stores u distinct chars.

### Tier 2: Toggle odd set

Toggle each character in a set of odd-count characters.

- Time: `O(n)` - Each character toggles set membership once.
- Space: `O(u)` - The set stores odd-count characters.
