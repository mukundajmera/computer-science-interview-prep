# Permutation in String

## Overview

Given strings `s1` and `s2`, determine whether any substring of `s2` is a permutation of `s1`.

This is a fixed-size frequency window. The window length is `len(s1)`, and validity means the active counts match the target counts.

## Requirements and constraints

- Return true if any contiguous substring of `s2` has the same multiset of characters as `s1`.
- Window size is fixed at `len(s1)`.
- Prefer `O(n)` time over `s2`.
- Space is `O(alphabet)` or `O(distinct(s1))`.

## High-level design / approach

1. Build target character counts from `s1`.
2. Slide a window of length `len(s1)` over `s2`.
3. Maintain active counts or a deficit map.
4. When the window reaches target length:
   - check whether all deficits are satisfied or matched count equals required distinct count;
   - remove the outgoing left character before expanding further.

Invariant: each full window represents exactly one candidate substring of length `len(s1)`.

## Dry run

Input: `s1 = "ab"`, `s2 = "eidbaooo"`.

| Window | Counts match `ab`? |
|---|---|
| `ei` | no |
| `id` | no |
| `db` | no |
| `ba` | yes |

The answer is true because `ba` is a permutation of `ab`.

## Language-neutral pseudocode

```text
need = counts(s1)
window = {}
left = 0
for right, ch in s2:
    window[ch] += 1
    if right - left + 1 > len(s1):
        window[s2[left]] -= 1
        if window[s2[left]] == 0: delete window[s2[left]]
        left += 1
    if right - left + 1 == len(s1) and window == need:
        return true
return false
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Fixed length | Maintains exactly `len(s1)` characters before comparison |
| Frequency equality | Avoids sorting each window |
| Matched count | Updates match status only when counts cross target boundaries |
| Complexity | `O(len(s1) + len(s2))` time |

## Common pitfalls

1. Sorting every candidate substring.
2. Comparing full maps for every window when alphabet is large.
3. Checking before the window has full length.
4. Mishandling count transitions when a character enters or leaves.

## Follow-up questions

1. How would you return all anagram start indices?
2. How does the solution change for Unicode or very large alphabets?
3. What if `s2` arrives as a stream and you can store only the last `len(s1)` characters?

## Variants and extensions

- Find all anagrams in a string.
- Minimum window substring.
- Detect required event multiset in a recent log window.

## Cross-links

- [Sliding Window Overview](./01-overview.md)
- [Longest Substring Without Repeating Characters](./04-longest-substring-without-repeating.md)
- [HLD Stream Processing](../../03-hld-concepts/stream-processing/THEORY.md)
- [Ad Click Aggregator HLD](../../04-hld-projects/ad-click-aggregator/)
