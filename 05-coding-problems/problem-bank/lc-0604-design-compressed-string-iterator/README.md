# Design Compressed String Iterator

- Canonical ID: `lc-0604-design-compressed-string-iterator`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Design an iterator over a run-length encoded string, returning the next character while run counts remain and a blank space when exhausted.

## Driver Signature

- Java class: `StringIterator`
- Python class: `StringIterator`
- Methods: `['next', 'hasNext']`

## Key Cases and Invariants

- Counts may contain multiple digits.
- The iterator must not expand huge runs unnecessarily in the optimized version.

## Solution Ladder

### Tier 1: Expanded string

Expand the compressed input into a full character array and iterate it.

- Time: `O(N)` - Construction expands all N output characters; each next is O(1).
- Space: `O(N)` - The expanded sequence is stored.

### Tier 2: Run parser

Parse one run at a time and decrement its remaining count lazily.

- Time: `O(L)` - Construction scans the compressed string once; next is amortized O(1).
- Space: `O(R)` - Runs are stored as character/count pairs.
