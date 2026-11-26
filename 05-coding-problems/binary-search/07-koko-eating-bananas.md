# Koko Eating Bananas

## Overview

Given piles of bananas and a number of hours `h`, find the minimum integer eating speed that lets all piles be finished within `h` hours.

This is binary search on the answer. The array is not searched directly. Instead, possible speeds form an ordered value range, and the feasibility predicate is monotonic: if speed `s` works, every speed greater than `s` also works.

## Requirements and constraints

- Speed must be a positive integer.
- Each pile takes `ceil(pile / speed)` hours.
- Return the smallest feasible speed.
- Prefer `O(n log max(pile))` time and `O(1)` space.
- Explain why the feasibility predicate is monotonic.

## High-level design / approach

1. Candidate speeds range from `1` to `max(piles)`.
2. Define `can_finish(speed)`:
   - sum `ceil(pile / speed)` for every pile;
   - return whether total hours are `<= h`.
3. Binary search the first feasible speed:
   - if `can_finish(mid)` is true, keep `mid` with `right = mid`;
   - otherwise set `left = mid + 1`.
4. Return `left`.

Invariant: every speed below `left` is known infeasible; at least one feasible speed remains in `[left, right]`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Search-space choice | Searches speeds, not pile indices |
| Monotonic proof | Larger speed never increases required hours |
| Feasibility cost | States each check scans all piles |
| Return semantics | Returns first feasible speed, not any feasible speed |

## Common pitfalls

1. Sorting piles even though order does not matter.
2. Searching pile indices instead of possible speeds.
3. Using floating-point ceiling instead of integer arithmetic.
4. Returning as soon as one feasible speed is found.
5. Misstating complexity as `O(log n)`.

## Follow-up questions

1. What if the objective is minimum capacity to ship packages within `D` days?
2. What if speed can be fractional?
3. How would you add a hard upper bound or impossible-case check?
4. How does this pattern show up in capacity planning?

## Variants and extensions

- Minimum shipping capacity within a deadline.
- Split array largest sum.
- Minimum machine throughput to clear a queue by a deadline.
- Smallest autoscaling fleet size satisfying a load test.

## Cross-links

- [Binary Search Overview](./01-overview.md)
- [HLD Load Balancing](../../03-hld-concepts/load-balancing/)
- [HLD Message Queues](../../03-hld-concepts/message-queues/THEORY.md)
- [HLD Long-Running Tasks](../../03-hld-concepts/long-running-tasks/)
