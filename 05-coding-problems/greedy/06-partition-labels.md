# Partition Labels

## Overview

Given a string, split it into as many parts as possible so each character appears in at most one part.

The greedy boundary is the farthest last occurrence of any character seen in the current segment.

## Requirements and constraints

- Return lengths of partitions.
- Each character must appear in only one partition.
- Prefer `O(n)` time.

## Recognition cue

"Partition so no symbol crosses partitions" signals last-occurrence boundary greedy.

## Invariant or state definition

`end` is the farthest last occurrence of any character seen in the current segment, so the segment cannot close before `end`.

## Proof idea

When scanning a segment, every character inside it forces the segment to extend at least to that character's last occurrence. Closing the segment before the maximum last occurrence would split a character across partitions. Closing exactly at that boundary is safe and maximizes the number of segments because delaying further only merges segments unnecessarily.

## Wrong greedy counterexample

Closing at the first repeated character fails. In `abac`, closing at `aba` because `a` repeats gives one segment of length `3`, but the real boundary is based on last occurrences of every character seen, not the first duplicate event.

## High-level design / approach

1. Precompute `last[char]`.
2. Scan the string.
3. Track `segment_end = max(segment_end, last[current_char])`.
4. When `i == segment_end`, close the segment.
5. Start the next segment at `i + 1`.

## Dry run

`s = "ababcbacadefegdehijhklij"`.

The first segment starts at `0`.

- `a` last appears at `8`, so segment must reach at least `8`.
- `b` last appears at `5`.
- `c` last appears at `7`.
- at `i = 8`, all characters seen so far end within the segment.

First partition length: `9`.

Full answer: `[9, 7, 8]`.

## Language-neutral pseudocode

```text
last = map each char to its last index
result = []
start = 0
end = 0
for i from 0 to len(s) - 1:
    end = max(end, last[s[i]])
    if i == end:
        result.append(end - start + 1)
        start = i + 1
return result
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Boundary | Uses last occurrence of all characters in segment |
| Greedy close | Closes as soon as the boundary is satisfied |
| Correctness | Explains why earlier close is invalid and later close is worse |
| Complexity | `O(n)` time, bounded char map space |

## Common pitfalls

1. Closing at the first repeated character.
2. Sorting characters and losing original order.
3. Forgetting to update boundary for every character inside the segment.
4. Returning substrings when the prompt asks for lengths.

## Follow-up questions

1. What if the alphabet is huge?
2. What if partitions have a maximum length?
3. How would this apply to log segments with tenant IDs?

## Variants and extensions

- Log compaction boundaries.
- Tenant-isolated batch segmentation.
- Build graph chunking where dependencies cannot cross chunks.

## Cross-links

- [Greedy Overview](./01-overview.md)
- [Content Moderation Platform](../../04-hld-projects/content-moderation-platform/)
