# First Bad Version

- Canonical ID: `lc-0278-first-bad-version`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Find the first version in a monotonic sequence where all versions at or after a hidden boundary are bad. The generated driver supplies that hidden boundary as `firstBad` to model the oracle.

## Driver Signature

- Java: `int firstBadVersion(int n, int firstBad)`
- Python: `firstBadVersion(n: int, firstBad: int) -> int`

## Key Cases and Invariants

- The predicate is false before the boundary and true from the boundary onward.
- Binary search must keep the first true position, not just any true version.
- The driver parameter `firstBad` models the hidden API response deterministically.

## Solution Ladder

### Tier 1: Linear scan

Check versions from left to right until the first bad version appears.

- Time: `O(n)` - The scan may inspect every version.
- Space: `O(1)` - Only loop counters are stored.

### Tier 2: Binary search

Use the monotonic predicate to shrink toward the first true version.

- Time: `O(log n)` - Each oracle check halves the remaining range.
- Space: `O(1)` - Only search bounds are stored.
