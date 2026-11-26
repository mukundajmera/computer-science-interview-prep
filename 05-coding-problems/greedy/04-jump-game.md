# Jump Game

## Overview

Given an array where `nums[i]` is the maximum jump length from index `i`, decide whether you can reach the last index.

The greedy invariant is the farthest reachable index seen so far.

## Requirements and constraints

- Return boolean reachability.
- Input values are non-negative.
- Canonical interview constraints have `n >= 1`; if the prompt allows an empty array, ask for semantics before coding instead of silently returning true.
- Prefer `O(n)` time and `O(1)` space.

## Recognition cue

"Can reach the end" with max jump lengths signals farthest-reach greedy.

## Proof idea

If index `i` is reachable, then any position up to `i + nums[i]` may become reachable. The only future-relevant fact is the maximum such boundary. If the scan reaches an index greater than that boundary, no previous index can jump over the gap, so the answer is false.

## High-level design / approach

1. Set `farthest = 0`.
2. For each index `i`:
   - if `i > farthest`, return false;
   - update `farthest = max(farthest, i + nums[i])`;
   - if `farthest >= last_index`, return true.
3. Return true after the scan.

## Dry run

`nums = [2, 3, 1, 1, 4]`.

| i | nums[i] | Before farthest | Reachable? | After farthest |
|---:|---:|---:|---|---:|
| 0 | 2 | 0 | yes | 2 |
| 1 | 3 | 2 | yes | 4 |

`farthest` reaches the last index, so answer is true.

Counterexample: `[3, 2, 1, 0, 4]`.

By index `3`, `farthest` is `3`; index `4` is beyond the boundary, so answer is false.

## Language-neutral pseudocode

```text
farthest = 0
for i from 0 to n - 1:
    if i > farthest:
        return false
    farthest = max(farthest, i + nums[i])
    if farthest >= n - 1:
        return true
return true
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Invariant | Farthest reachable index after scanning reachable positions |
| Impossible case | Detects first gap where `i > farthest` |
| Complexity | One pass, constant extra space |
| Proof | Explains why only farthest boundary matters |

## Common pitfalls

1. Trying every jump recursively and timing out.
2. Updating from unreachable indexes.
3. Returning false too early before scanning all reachable options.
4. Confusing this decision problem with minimum jumps.

## Follow-up questions

1. How would you compute the minimum number of jumps?
2. What if jumps have costs?
3. What if negative jumps are allowed?

## Variants and extensions

- Minimum jumps, which needs a different `current_end` / `current_farthest` / `jumps` invariant.
- Coverage with intervals.
- Service failover reachability through ordered fallback layers.

## Cross-links

- [Greedy Overview](./01-overview.md)
- [Load Balancing](../../03-hld-concepts/load-balancing/THEORY.md)
