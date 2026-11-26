# Minimum Arrows to Burst Balloons

## Overview

Given balloon intervals on a number line, return the minimum number of arrows needed to burst all balloons. One arrow shot at position `x` bursts every interval containing `x`.

The greedy rule is: sort by end coordinate and shoot an arrow at the earliest possible end of the first uncovered balloon.

## Requirements and constraints

- Intervals are inclusive.
- Return the minimum arrow count.
- Prefer `O(n log n)` time and `O(1)` extra space.

## Recognition cue

"Minimum points to cover intervals" signals endpoint coverage greedy.

## Invariant or state definition

`arrow_pos` is the end of the earliest-ending uncovered balloon chosen for the current arrow, and all scanned balloons before the current interval are covered.

## Proof idea

For the first uncovered balloon, any valid solution must shoot an arrow somewhere inside it. Shooting at its end is at least as good as shooting earlier, because the end is the latest point that still covers this balloon and may also cover more future balloons. Sorting by end ensures this choice leaves maximum chance to cover following intervals.

## Wrong greedy counterexample

Shooting at each interval's start can overcount. For `[1,10], [2,3], [4,5]`, choosing starts independently misses the fact that the correct endpoint choices can cover compact overlapping groups.

## High-level design / approach

1. Sort intervals by end ascending.
2. Initialize `arrows = 0` and `arrow_pos = none`.
3. For each interval:
   - if it is already covered by `arrow_pos`, continue;
   - otherwise shoot a new arrow at this interval's end.
4. Return `arrows`.

## Dry run

Balloons: `[10,16], [2,8], [1,6], [7,12]`.

Sorted by end: `[1,6], [2,8], [7,12], [10,16]`.

| Balloon | Decision | Arrow position | Arrows |
|---|---|---:|---:|
| `[1,6]` | shoot | 6 | 1 |
| `[2,8]` | covered | 6 | 1 |
| `[7,12]` | shoot | 12 | 2 |
| `[10,16]` | covered | 12 | 2 |

Answer: `2`.

## Language-neutral pseudocode

```text
sort intervals by end ascending
arrows = 0
arrow_pos = none
for interval in intervals:
    if arrow_pos is none or interval.start > arrow_pos:
        arrows += 1
        arrow_pos = interval.end
return arrows
```

Use `start > arrow_pos` for inclusive intervals. For half-open intervals, the condition changes.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Sort key | Sorts by end coordinate |
| Coverage condition | Uses inclusive endpoint rule correctly |
| Proof | Explains why shooting at earliest end is safe |
| Complexity | `O(n log n)` sort plus one scan |

## Common pitfalls

1. Sorting by start without shrinking the active overlap end, which can overcount.
2. Shooting at interval midpoint without proof.
3. Using `>=` when intervals are inclusive.
4. Forgetting empty input.

## Follow-up questions

1. What changes if intervals are half-open?
2. How would you return arrow positions?
3. What if arrows have different costs or capacities?

## Variants and extensions

- Minimum cameras to cover road segments.
- CDN edge placement for contiguous regions.
- Batch windows covered by a single processing job.

## Cross-links

- [Greedy Overview](./01-overview.md)
- [Caching](../../03-hld-concepts/caching/THEORY.md)
- [Load Balancing](../../03-hld-concepts/load-balancing/THEORY.md)
