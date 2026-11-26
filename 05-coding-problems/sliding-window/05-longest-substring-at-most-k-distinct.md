# Longest Substring With At Most K Distinct Characters

## Overview

Given a string and integer `k`, find the length of the longest substring containing at most `k` distinct characters.

This teaches the most reusable frequency-map window: expand until invalid, shrink until valid, and record the best valid length.

## Requirements and constraints

- Return maximum length.
- `k` may be zero.
- Substring must be contiguous.
- Prefer `O(n)` time.
- Space is `O(min(k, alphabet))` for the active frequency map.

## High-level design / approach

1. Initialize `left = 0`, an empty frequency map, and `best = 0`.
2. Expand `right`; increment the count for `s[right]`.
3. While the map has more than `k` keys:
   - decrement `s[left]`;
   - remove the key if the count reaches zero;
   - move `left`.
4. The window is valid; update `best`.

Invariant: after the shrink loop, the active map exactly represents characters in `[left, right]`, and the number of keys is at most `k`.

## Dry run

Input: `s = "eceba"`, `k = 2`.

| Right | Char | Repair | Window | Best |
|---:|---|---|---|---:|
| 0 | `e` | none | `e` | 1 |
| 1 | `c` | none | `ec` | 2 |
| 2 | `e` | none | `ece` | 3 |
| 3 | `b` | remove `e`, then `c` | `eb` | 3 |
| 4 | `a` | remove `e` | `ba` | 3 |

## Language-neutral pseudocode

```text
left = 0
freq = {}
best = 0
for right, ch in s:
    freq[ch] += 1
    while size(freq) > k:
        freq[s[left]] -= 1
        if freq[s[left]] == 0:
            delete freq[s[left]]
        left += 1
    best = max(best, right - left + 1)
return best
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Frequency map | Maintains exact active counts |
| Distinct count | Removes zero-count keys or tracks distinct separately |
| Edge handling | Handles `k = 0`, empty string, and large `k` |
| Complexity | `O(n)` time, `O(min(k, alphabet))` space |

## Common pitfalls

1. Leaving zero-count keys in the map.
2. Shrinking only once when several removals are needed.
3. Recording the answer while the window still has more than `k` distinct characters.
4. Confusing "at most K" with "exactly K".

## Follow-up questions

1. How do you adapt this to at most K replacements?
2. How do you count all substrings with at most K distinct characters?
3. How does memory change for arbitrary Unicode vs lowercase English letters?

## Variants and extensions

- Longest substring with at most two distinct characters.
- Longest repeating character replacement.
- Count subarrays with exactly K distinct values.

## Cross-links

- [Sliding Window Overview](./01-overview.md)
- [Longest Substring Without Repeating Characters](./04-longest-substring-without-repeating.md)
- [Subarrays With Exactly K Distinct](./06-subarrays-with-exactly-k-distinct.md)
- [Realtime Metrics Platform HLD](../../04-hld-projects/realtime-metrics-platform/)
