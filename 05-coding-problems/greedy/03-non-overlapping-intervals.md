# Non-overlapping Intervals

## Overview

Given intervals, return the minimum number to remove so the rest do not overlap.

This is the removal version of activity selection. Maximize intervals kept by earliest finish, then removals equal `n - kept`.

## Requirements and constraints

- Clarify whether `[1,2]` and `[2,3]` overlap.
- Return minimum removals, not the remaining list unless asked.
- Sort once and scan.

## Recognition cue

"Minimum intervals to remove" plus "remaining intervals do not overlap" signals keep-as-many-as-possible greedy.

## Invariant or state definition

After each scan step, the kept intervals are compatible and `last_end` is as small as possible for the number of intervals kept so far.

## Proof idea

Removing the fewest intervals is equivalent to keeping the most compatible intervals. Earliest-finish greedy keeps the maximum number by the same exchange proof as activity selection.

## Wrong greedy counterexample

Keeping the earliest starting interval can fail. For `[1,100], [2,3], [3,4], [4,5]`, keeping `[1,100]` first forces three removals, while earliest-finish keeps the three short compatible intervals and removes only one.

## High-level design / approach

1. Sort intervals by end time.
2. Keep a `last_end` for the last interval kept.
3. If the next interval starts after or at `last_end`, keep it.
4. Otherwise remove it.
5. Return removal count.

## Dry run

Intervals: `[1,2], [2,3], [3,4], [1,3]`.

Sorted by end: `[1,2], [2,3], [1,3], [3,4]`.

| Interval | Decision | `last_end` | Removals |
|---|---|---:|---:|
| `[1,2]` | keep | 2 | 0 |
| `[2,3]` | keep | 3 | 0 |
| `[1,3]` | remove | 3 | 1 |
| `[3,4]` | keep | 4 | 1 |

Answer: `1`.

## Language-neutral pseudocode

```text
sort intervals by end ascending
removed = 0
last_end = -infinity
for interval in intervals:
    if interval.start >= last_end:
        last_end = interval.end
    else:
        removed += 1
return removed
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Equivalence | Connects minimum removals to maximum kept intervals |
| Sort key | Uses end time to preserve future space |
| Tie handling | Handles equal endpoints consistently |
| Complexity | `O(n log n)` time, `O(1)` extra space |

## Common pitfalls

1. Sorting by start and removing the wrong interval on conflict.
2. Keeping the longer interval because it starts first.
3. Forgetting empty or single-interval input.
4. Treating touching endpoints incorrectly.

## Follow-up questions

1. What changes if intervals have weights?
2. How would you output the remaining intervals?
3. How does this differ from merging intervals?

## Variants and extensions

- Minimum meeting cancellations.
- Maximum compatible reservations.
- Cleanup of overlapping alert windows.

## Cross-links

- [Activity Selection](./02-activity-selection.md)
- [Pattern to System Design Map](../PATTERN-SD-MAP.md)
- [Ticketing Platform HLD](../../04-hld-projects/ticketing-platform/)
