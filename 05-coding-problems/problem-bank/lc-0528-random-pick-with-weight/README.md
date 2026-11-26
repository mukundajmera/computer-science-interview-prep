# Random Pick with Weight

- Canonical ID: `lc-0528-random-pick-with-weight`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Design a picker that returns an index randomly with probability proportional to that index's positive weight.

## Driver Signature

- Java class: `Solution`
- Python class: `Solution`
- Methods: `['pickIndex']`

## Key Cases and Invariants

- Prefix sums convert weights into contiguous numeric ranges.
- Binary search maps a sampled point to its owning range.
- Generated tests validate deterministic invariants and single-choice cases rather than statistical distribution.

## Solution Ladder

### Tier 1: Expanded bag

Materialize each index weight times and choose a random slot.

- Time: `O(W)` - Construction expands total weight W; each pick is O(1).
- Space: `O(W)` - The bag stores one entry per unit of weight.

### Tier 2: Prefix binary search

Store cumulative weights and binary-search the sampled point.

- Time: `O(log n)` - Each pick performs one binary search over n prefixes.
- Space: `O(n)` - Prefix sums store one value per index.
