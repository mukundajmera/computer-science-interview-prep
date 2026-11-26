# Longest Substring Without Repeating Characters

## Overview

Given a string, find the length of the longest contiguous substring with no repeated characters.

This is the canonical variable-window string problem. The window is valid while every character count is at most one.

## Requirements and constraints

- Return the maximum valid length.
- The substring must be contiguous.
- Prefer `O(n)` time.
- Space is `O(alphabet)` for the character map or last-seen table.
- Unicode handling depends on interview scope; state whether the input is ASCII, lowercase, or arbitrary characters.

## High-level design / approach

Use either count-map shrink or last-seen jump.

Count-map approach:

1. Expand `right` and increment the character count.
2. While the new character has count greater than one:
   - decrement `s[left]`;
   - move `left`.
3. The window is now valid; update `best`.

Invariant: after the shrink loop, every character in `[left, right]` appears at most once.

## Dry run

Input: `s = "abca"`.

| Right | Char | Repair | Window | Best |
|---:|---|---|---|---:|
| 0 | `a` | none | `a` | 1 |
| 1 | `b` | none | `ab` | 2 |
| 2 | `c` | none | `abc` | 3 |
| 3 | `a` | remove old `a` | `bca` | 3 |

## Language-neutral pseudocode

```text
left = 0
counts = {}
best = 0
for right, ch in s:
    counts[ch] += 1
    while counts[ch] > 1:
        counts[s[left]] -= 1
        left += 1
    best = max(best, right - left + 1)
return best
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Validity predicate | No character count exceeds one |
| Shrink logic | Shrinks only until the duplicate is removed |
| State cleanup | Maintains counts or last-seen indices consistently |
| Complexity | `O(n)` time because each character enters/leaves once |

## Common pitfalls

1. Resetting the whole window when a duplicate appears.
2. Moving `left` backward with stale last-seen indexes.
3. Forgetting to update `best` after restoring validity.
4. Claiming constant space without clarifying alphabet bounds.

## Follow-up questions

1. How does the last-seen index solution avoid repeated shrink loops?
2. What changes if the string contains Unicode grapheme clusters?
3. How would you return the substring, not just the length?

## Variants and extensions

- Longest substring with at most K distinct characters.
- Longest substring after replacing at most K characters.
- Session dedupe in a recent activity window.

## Cross-links

- [Sliding Window Overview](./01-overview.md)
- [Longest Substring With At Most K Distinct](./05-longest-substring-at-most-k-distinct.md)
- [Permutation in String](./07-permutation-in-string.md)
- [HLD Stream Processing](../../03-hld-concepts/stream-processing/THEORY.md)
