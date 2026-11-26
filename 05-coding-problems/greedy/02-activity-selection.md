# Activity Selection

## Overview

Given intervals with start and end times, select the maximum number of non-overlapping activities.

The greedy rule is: sort by end time and always take the next activity whose start is at or after the last chosen end.

## Requirements and constraints

- Intervals are half-open or closed depending on prompt wording; clarify whether `end == start` is allowed.
- Return count or selected activities.
- Prefer `O(n log n)` time for sorting and `O(1)` extra space beyond output.

## Recognition cue

"Maximum number of meetings/events/jobs that do not overlap" strongly signals earliest-finish greedy.

## Invariant or state definition

After each accepted activity, `last_end` is the earliest possible finishing boundary among all schedules with the same number of accepted activities.

## Proof idea

Earliest finish is safe by exchange.

Take an optimal solution. Let its first chosen interval be `x`. If the greedy interval `g` ends no later than `x`, replace `x` with `g`. The replacement does not overlap any later interval that was compatible with `x`, because `g` frees at least as much remaining time. So some optimal solution starts with `g`.

## Wrong greedy counterexample

Sorting by shortest duration fails. For half-open intervals `[1,4], [4,7], [3,5]`, duration-first takes the short middle interval `[3,5]` and blocks both compatible longer intervals. Earliest-finish keeps `[1,4]` and `[4,7]`, so it gets two activities instead of one.

## High-level design / approach

1. Sort intervals by `end` ascending.
2. Track `last_end`.
3. For each interval in sorted order:
   - if `start >= last_end`, select it and set `last_end = end`;
   - otherwise skip it.
4. Return selected intervals or count.

## Dry run

Intervals: `[1,4], [2,3], [3,5], [0,6], [5,7], [8,9]`.

Sorted by end: `[2,3], [1,4], [3,5], [0,6], [5,7], [8,9]`.

| Interval | Decision | Reason | Selected |
|---|---|---|---|
| `[2,3]` | take | earliest finish | `[2,3]` |
| `[1,4]` | skip | starts before 3 | `[2,3]` |
| `[3,5]` | take | starts at 3 | `[2,3], [3,5]` |
| `[0,6]` | skip | starts before 5 | same |
| `[5,7]` | take | starts at 5 | add `[5,7]` |
| `[8,9]` | take | starts after 7 | add `[8,9]` |

Answer count: `4`.

## Language-neutral pseudocode

```text
sort intervals by end ascending
selected = []
last_end = -infinity
for interval in intervals:
    if interval.start >= last_end:
        selected.append(interval)
        last_end = interval.end
return selected
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Sort key | Sorts by end time, not start time |
| Proof | Gives exchange argument |
| Boundary | Clarifies whether touching endpoints overlap |
| Complexity | `O(n log n)` sorting, linear scan |

## Common pitfalls

1. Sorting by shortest duration.
2. Sorting by earliest start.
3. Forgetting endpoint convention.
4. Returning skipped intervals when the prompt asks for selected intervals.

## Follow-up questions

1. How would you return the removed intervals instead?
2. What if every interval has a profit?
3. What if rooms are unlimited and you need minimum rooms?

## Variants and extensions

- Meeting scheduling.
- CPU job windows.
- Ad campaign time-slot selection.
- Reservation conflict pruning.

## Cross-links

- [Greedy Overview](./01-overview.md)
- [Job Scheduler HLD](../../04-hld-projects/job-scheduler/)
- [Quick Commerce Delivery HLD](../../04-hld-projects/quick-commerce-delivery/)
