# Distinct Subsequences

- Canonical ID: `lc-0115-distinct-subsequences`
- Difficulty: `hard`
- Status: `verified`

## Clean-Room Problem Summary

Count how many distinct subsequences of a source string equal a target string.

## Driver Signature

- Java: `int numDistinct(String s, String t)`
- Python: `numDistinct(s: str, t: str) -> int`

## Key Cases and Invariants

- Skipping a source character and using a matching source character are separate choices.
- An empty target has exactly one subsequence: choose nothing.

## Solution Ladder

### Tier 1: Recursive memoization

Memoize `(i, j)` choices for source suffix and target suffix.

- Time: `O(mn)` - Each source/target suffix pair is solved once.
- Space: `O(mn)` - Memo entries dominate recursion stack storage.

### Tier 2: One-dimensional DP

Scan source characters and update target-prefix counts from right to left.

- Time: `O(mn)` - Each source character updates each target position.
- Space: `O(n)` - The DP array stores counts for target prefixes.
