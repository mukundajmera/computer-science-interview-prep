# Word Break

## Overview

Given a string and a dictionary of words, determine whether the string can be segmented into a sequence of dictionary words.

This is feasibility DP over prefixes. A prefix is valid if it can be split at some earlier valid prefix and the suffix is a dictionary word.

## Requirements and constraints

- Dictionary words may be reused.
- Return boolean feasibility.
- Prefer using a set for dictionary lookup.
- State the substring-check cost if relevant.

## Recognition cue

"Can segment", "dictionary words", and "prefix can be formed" signal boolean DP.

## State definition

`dp[i]` is true if `s[:i]` can be segmented into dictionary words.

## High-level design / approach

1. Put words in a set.
2. Set `dp[0] = true` for the empty prefix.
3. For each end index `i`, try every split point `j < i`.
4. If `dp[j]` is true and `s[j:i]` is in the dictionary, set `dp[i] = true`.
5. Return `dp[n]`.

## Dry run

`s = "leetcode"`, dictionary: `leet`, `code`.

| `i` | Prefix | Successful split | `dp[i]` |
|---:|---|---|---|
| 0 | empty | base | true |
| 1 | `l` | none; `dp[0] + "l"` is not a word | false |
| 2 | `le` | none; candidate suffixes are not dictionary words | false |
| 3 | `lee` | none; no valid split ends here | false |
| 4 | `leet` | `dp[0]` + `leet` | true |
| 5 | `leetc` | none; `dp[4] + "c"` is not a word | false |
| 6 | `leetco` | none; no valid suffix after a true prefix | false |
| 7 | `leetcod` | none; no valid suffix after a true prefix | false |
| 8 | `leetcode` | `dp[4]` + `code` | true |

Answer: `true`.

## Language-neutral pseudocode

```text
words = set(wordDict)
dp = array length n + 1 filled false
dp[0] = true
for i from 1 to n:
    for j from 0 to i - 1:
        if dp[j] and s[j:i] in words:
            dp[i] = true
            break
return dp[n]
```

## Complexity proof

The table has `n + 1` states. For each end index `i`, the simple implementation tries up to `i` split points, so the loop count is `O(n^2)`. If dictionary membership checks use string slices that copy `s[j:i]`, each check can cost up to `O(n)`, making the worst case `O(n^3)` in those languages.

You can tighten the bound by only trying word lengths that exist in the dictionary, limiting splits to the maximum word length, or using a trie to scan candidate suffixes without repeatedly allocating substrings. Space is `O(n)` for `dp` plus dictionary storage.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| State | Defines feasibility of a prefix |
| Base case | Uses empty prefix as true |
| Transition | Combines valid earlier prefix with dictionary suffix |
| Complexity | States loop and substring lookup costs honestly |

## Common pitfalls

1. Starting with `dp[0] = false`.
2. Checking only dictionary words from the beginning.
3. Forgetting repeated word use is allowed.
4. Ignoring substring creation cost in languages where slicing copies.

## Follow-up questions

1. How would you return one valid segmentation?
2. How would you count all segmentations?
3. How would a trie reduce candidate checks?

## Variants and extensions

- Decode ways.
- Sentence segmentation.
- Tokenization and command parsing.

## Cross-links

- [Dynamic Programming Overview](./01-overview.md)
- [Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
