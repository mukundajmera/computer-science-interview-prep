# Task Scheduler

- Canonical ID: `lc-0621-task-scheduler`
- Difficulty: `medium`
- Status: `verified`

## Clean-Room Problem Summary

Given task labels and a cooldown, compute the minimum number of time slots needed to run every task while keeping identical labels at least the cooldown distance apart.

## Driver Signature

- Java: `int leastInterval(char[] tasks, int n)`
- Python: `leastInterval(tasks: List[str], n: int) -> int`

## Key Cases and Invariants

- Different labels can run in adjacent slots.
- Idle time is needed only when the most frequent tasks leave unavoidable gaps.
- When many other tasks fill the gaps, the answer is just the number of tasks.

## Solution Ladder

### Tier 1: Heap cycle simulation

Repeatedly schedule up to n + 1 currently most frequent task labels, reinserting labels that still have work.

- Time: `O(T log U)` - T scheduled/idle slots each touch a heap of U distinct labels.
- Space: `O(U)` - The heap stores one counter per label.

### Tier 2: Frequency frame formula

Use the maximum frequency to count mandatory frames, then compare against the raw task count.

- Time: `O(T + U)` - Count tasks once and scan the U label counts.
- Space: `O(U)` - Frequency counts are stored for distinct labels.
