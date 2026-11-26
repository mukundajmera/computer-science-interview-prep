# Gas Station

## Overview

Given `gas[i]` and `cost[i]` around a circular route, return the starting station index if you can complete the circuit, else `-1`.

The greedy insight: if total gas is enough and a segment from `start` to `i` goes negative, no station inside that failed segment can be a valid start.

## Requirements and constraints

- Return one valid start index.
- Return `-1` if impossible.
- Arrays have equal length.
- Canonical interview constraints have `n >= 1`; if an empty route is allowed, return `-1` or the agreed no-op value explicitly.
- Prefer `O(n)` time and `O(1)` space.

## Recognition cue

"Complete a circular route" with net gain/loss at each station signals prefix-balance greedy.

## Invariant or state definition

`start` is the first station after the latest failed negative-balance segment; every station before `start` has already been proven invalid.

## Proof idea

If the running tank from `start` through station `i` becomes negative, then every candidate between `start` and `i` also fails before or at `i`. Those candidates start with less accumulated surplus than `start` had, so they cannot overcome the same deficit. The next possible start is `i + 1`.

If total gas is negative, no start can work.

## Wrong greedy counterexample

Starting at the station with the largest individual surplus is not a proof. A large local surplus can still be followed by a deficit that only a different earlier accumulated balance can survive. The reset proof is about failed prefixes, not the best-looking station.

## High-level design / approach

1. Track `total_balance` across all stations.
2. Track `tank` from current candidate start.
3. When `tank` becomes negative:
   - set `start = i + 1`;
   - reset `tank = 0`.
4. After scan, return `start` if `total_balance >= 0`, else `-1`.

## Dry run

`gas = [1, 2, 3, 4, 5]`, `cost = [3, 4, 5, 1, 2]`.

Net: `[-2, -2, -2, 3, 3]`.

| i | net | tank | Action |
|---:|---:|---:|---|
| 0 | -2 | -2 | fail, next start 1 |
| 1 | -2 | -2 | fail, next start 2 |
| 2 | -2 | -2 | fail, next start 3 |
| 3 | 3 | 3 | keep start 3 |
| 4 | 3 | 6 | keep start 3 |

Total net is `0`, so answer is `3`.

## Language-neutral pseudocode

```text
if n == 0:
    return -1
total = 0
tank = 0
start = 0
for i from 0 to n - 1:
    net = gas[i] - cost[i]
    total += net
    tank += net
    if tank < 0:
        start = i + 1
        tank = 0
return start if total >= 0 else -1
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Feasibility | Checks total balance |
| Reset proof | Explains why skipped starts cannot work |
| Circularity | Avoids simulating from every station |
| Complexity | One pass and constant space |

## Common pitfalls

1. Trying every start for `O(n^2)`.
2. Returning `start` without checking total balance.
3. Resetting start on `tank == 0` instead of only negative.
4. Failing to explain why skipped stations are invalid.

## Follow-up questions

1. What if there can be multiple starts?
2. What if tank capacity is limited?
3. How does the proof change if route order can be rearranged?

## Variants and extensions

- Delivery route feasibility.
- Provider fallback budget.
- Token-bucket deficit recovery.

## Cross-links

- [Greedy Overview](./01-overview.md)
- [Quick Commerce Delivery HLD](../../04-hld-projects/quick-commerce-delivery/)
