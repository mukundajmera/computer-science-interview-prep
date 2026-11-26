# Employee Free Time

- Canonical ID: `lc-0759-employee-free-time`
- Difficulty: `hard`
- Status: `verified`

## Clean-Room Problem Summary

Given each employee's sorted busy intervals, return finite intervals when every employee is free.

## Driver Signature

- Java: `int[][] employeeFreeTime(int[][][] schedule)`
- Python: `employeeFreeTime(schedule: List[List[List[int]]]) -> List[List[int]]`

## Key Cases and Invariants

- Intervals are represented as `[start, end]` pairs in the generated driver.
- Merging all busy intervals reveals gaps where no employee is busy.
- A heap can stream the next earliest interval without flattening every list first.

## Solution Ladder

### Tier 1: Flatten and merge

Flatten all busy intervals, sort by start, and record gaps between merged busy ranges.

- Time: `O(N log N)` - All N intervals are sorted.
- Space: `O(N)` - Flattened intervals are stored before merging.

### Tier 2: Min heap stream

Push each employee's first interval into a heap, streaming intervals by start time and recording gaps.

- Time: `O(N log E)` - Each interval enters and leaves a heap of E employees once.
- Space: `O(E)` - The heap stores at most one interval per employee.
