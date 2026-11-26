# Time Based Key-Value Store

- Canonical ID: `lc-0981-time-based-key-value-store`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Design a store that records string values by key and timestamp. A lookup asks for the newest value for that key whose timestamp is not greater than the query timestamp, or an empty string when no such value exists.

## Driver Signature

- Java class: `TimeMap`
- Python class: `TimeMap`
- Constructor parameters: `[]`
- Methods: `['set', 'get']`

## Key Cases and Invariants

- Each key keeps its own timestamp history.
- A query between two updates must return the earlier visible value.
- Missing keys and timestamps before the first update return an empty string.

## Solution Ladder

### Tier 1: Linear history scan

Keep every key history in insertion order and scan backward for the first visible timestamp.

- Time: `O(m)` - A get may inspect every version for that key.
- Space: `O(n)` - All set calls are retained.

### Tier 2: Binary search history

Keep each key's timestamp history sorted by append order and binary-search the rightmost visible timestamp.

- Time: `O(log m)` - A get performs one binary search over that key's m versions.
- Space: `O(n)` - All set calls are retained.
