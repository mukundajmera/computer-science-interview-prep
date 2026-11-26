# Task Scheduler

## Overview

Given tasks represented by labels and a cooldown `n`, return the minimum number of intervals needed so the same task label appears at least `n` intervals apart.

The heap-driven simulation uses a max-heap for task counts and a cooldown queue for tasks that were used but are not yet available.

## Requirements and constraints

- Each interval can run one task or idle.
- Same labels must be separated by at least `n` other intervals.
- The objective is minimum total time, not the actual schedule unless requested.
- A math formula exists for the common LeetCode version, but the heap simulation is easier to generalize.

## Recognition cue

"Most frequent task", "cooldown", "least intervals", and "choose next available task" signal a max-heap plus cooldown state.

## Invariant or state definition

At each time, the max-heap contains only tasks that are available to run now, ordered by remaining count. The cooldown queue contains tasks with their next allowed time.

## High-level design / approach

1. Count task frequencies.
2. Push all counts into a max-heap.
3. Advance time one interval at a time while work is available; if the heap is empty, jump directly to the next cooldown release time.
4. Move tasks from cooldown back to heap when their release time arrives.
5. If heap is non-empty, pop the highest-count task and run it.
6. If it still has remaining count, place it into cooldown with release time `time + n + 1`.
7. If heap is empty but cooldown is not, count the idle span by moving `time` to the next release instead of ticking through every idle slot.

## Dry run

Tasks: `A A A B B B`, cooldown `2`.

| Time | Available | Run | Cooldown after run |
|---:|---|---|---|
| 1 | `A3, B3` | A | A2 ready at 4 |
| 2 | `B3` | B | B2 ready at 5 |
| 3 | empty | idle | A ready at 4, B ready at 5 |
| 4 | `A2` | A | A1 ready at 7 |
| 5 | `B2` | B | B1 ready at 8 |
| 6 | empty | idle | A ready at 7, B ready at 8 |
| 7 | `A1` | A | none |
| 8 | `B1` | B | none |

Minimum intervals: `8`.

## Language-neutral pseudocode

```text
counts = frequency_map(tasks)
heap = max_heap of counts
cooldown = queue of (ready_time, remaining_count)
time = 0
while heap not empty or cooldown not empty:
    if heap is empty and cooldown is not empty and cooldown.front.ready_time > time:
        time = cooldown.front.ready_time
    else:
        time += 1

    while cooldown not empty and cooldown.front.ready_time <= time:
        heap.push(cooldown.pop_front().remaining_count)
    if heap not empty:
        count = heap.pop_max() - 1
        if count > 0:
            cooldown.push_back((time + n + 1, count))
return time
```

## Complexity proof

Let `T` be number of tasks and `U` be number of unique task labels. Counting costs `O(T)`. Each executed task causes heap operations over at most `U` labels, so the jump-ahead simulation is `O(T log U)`; a one-tick-at-a-time simulation would be `O(T log U + idle_time)`. Space is `O(U)` for counts, heap, and cooldown. For the fixed uppercase-letter variant, `U` is bounded by 26.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Availability | Does not run tasks still cooling down |
| Priority | Runs highest remaining available count |
| Release time | Uses `time + n + 1` consistently |
| Idle handling | Jumps to the next release when no task is available |
| Complexity | Distinguishes tasks, unique labels, and idle simulation |

## Common pitfalls

1. Reinsert task immediately after running it.
2. Using `time + n` instead of the correct next allowed slot.
3. Forgetting idle time.
4. Ticking through huge idle spans instead of jumping to the next release.
5. Losing labels when the actual schedule is requested.

## Follow-up questions

1. How would you return one valid schedule?
2. How does the closed-form formula work?
3. What if cooldown differs per task type?
4. How would priorities or deadlines change the design?

## Variants and extensions

- CPU task scheduling with cooldowns.
- Rate-limited job dispatch.
- Provider retry throttling.
- Campaign send spacing.

## Cross-links

- [Heap / Priority Queue Overview](./01-overview.md)
- [Reorganize String](./07-reorganize-string.md)
- [Job Scheduler HLD](../../04-hld-projects/job-scheduler/)
- [Rate Limiting](../../03-hld-concepts/rate-limiting/THEORY.md)
