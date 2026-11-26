# Append Characters to String to Make Subsequence

- Canonical ID: `lc-2486-append-characters-to-string-to-make-subsequence`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Return how many trailing characters must be appended to the source string so the target string becomes a subsequence.

## Driver Signature

- Java: `int appendCharacters(String s, String t)`
- Python: `appendCharacters(s: str, t: str) -> int`

## Key Cases and Invariants

- Only unmatched suffix characters of the target need appending.
- A two-pointer scan finds the longest target prefix already matched.

## Solution Ladder

### Tier 1: Repeated find

For each target character, search forward in the source from the current source position.

- Time: `O(|s||t|)` - Each target step may scan a source suffix.
- Space: `O(1)` - Only two positions are stored.

### Tier 2: Two pointer

Scan the source once and advance the target pointer whenever characters match.

- Time: `O(|s| + |t|)` - Each pointer moves forward only.
- Space: `O(1)` - Only pointer counters are stored.
