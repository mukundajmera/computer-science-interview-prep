# Regular Expression Matching

- Canonical ID: `lc-0010-regular-expression-matching`
- Difficulty: `hard`
- Status: `verified`

## Clean-Room Problem Summary

Check whether an entire text string matches a pattern where `.` matches one character and `*` repeats the previous pattern token zero or more times.

## Driver Signature

- Java: `boolean isMatch(String s, String p)`
- Python: `isMatch(s: str, p: str) -> bool`

## Key Cases and Invariants

- Matching must consume the whole string, not just a prefix.
- `x*` can either be skipped or consume one matching character and stay on the same pattern token.
- Empty text can still match a pattern made only of starred tokens.

## Solution Ladder

### Tier 1: Recursive memoization

Define a state `(i, j)` for text suffix `s[i:]` and pattern suffix `p[j:]`; memoize the skip-or-consume decisions around `*`.

- Time: `O(mn)` - There are at most `(m + 1) * (n + 1)` text/pattern states and each state does constant transition work.
- Space: `O(mn)` - The memo table and recursion stack store state results; the stack depth is bounded by `m + n` and the table dominates.

### Tier 2: Bottom-up DP

Fill the same state table from the end of the text and pattern toward the beginning.

- Time: `O(mn)` - Every state in the DP table is computed once.
- Space: `O(mn)` - The boolean table stores all suffix-match answers.
