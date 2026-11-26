# Longest Common Subsequence

## Overview

Given two strings, return the length of their longest common subsequence. Characters must appear in order but do not need to be contiguous.

This is the classic 2D sequence DP problem because each state compares prefixes of both strings.

## Requirements and constraints

- Preserve order in both strings.
- Characters can be skipped.
- Return length unless the prompt asks for the sequence.
- Prefer `O(m * n)` time.

## Recognition cue

"Two strings", "subsequence", and "longest common" signal prefix-pair DP.

## State definition

`dp[i][j]` is the LCS length between `text1[:i]` and `text2[:j]`.

## High-level design / approach

1. Create a `(m + 1) x (n + 1)` table initialized to `0`.
2. Iterate `i` from `1..m` and `j` from `1..n`.
3. If the current characters match, extend the smaller-prefix result:
   - `dp[i][j] = dp[i - 1][j - 1] + 1`.
4. If they do not match, skip one side:
   - `dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])`.
5. Return `dp[m][n]`.

## Dry run

`text1 = "abcde"`, `text2 = "ace"`.

| Prefix pair | Match? | Result |
|---|---|---:|
| `a` vs `a` | yes | 1 |
| `ab` vs `a` | no, skip `b` | 1 |
| `abc` vs `ac` | yes on `c` | 2 |
| `abcde` vs `ace` | yes on `e` | 3 |

Answer: `3` for `"ace"`.

## Language-neutral pseudocode

```text
dp = matrix (m + 1) by (n + 1) filled with 0
for i from 1 to m:
    for j from 1 to n:
        if text1[i - 1] == text2[j - 1]:
            dp[i][j] = dp[i - 1][j - 1] + 1
        else:
            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
return dp[m][n]
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| State | Defines prefixes, not suffixes by accident |
| Match case | Uses diagonal plus one |
| Mismatch case | Takes max of skipping either string |
| Complexity | `O(m * n)` time and space; can mention row compression |

## Common pitfalls

1. Treating it as substring and resetting on mismatch.
2. Indexing characters without padding the table.
3. Forgetting that empty prefix has LCS length zero.
4. Using a greedy two-pointer match and missing better subsequences.

## Follow-up questions

1. How would you reconstruct the LCS string?
2. How would you reduce space to `O(min(m, n))`?
3. How does edit distance relate to this table shape?

## Variants and extensions

- Edit distance.
- Shortest common supersequence.
- Diff tools and sequence alignment.

## Cross-links

- [Dynamic Programming Overview](./01-overview.md)
- [Two Pointers Pattern Pack](../two-pointers/README.md)
