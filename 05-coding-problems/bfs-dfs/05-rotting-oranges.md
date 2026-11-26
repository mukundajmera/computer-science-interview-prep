# Rotting Oranges

## Overview

Given a grid with empty cells, fresh oranges, and rotten oranges, return the minutes until all fresh oranges rot. Rotten oranges rot adjacent fresh oranges each minute.

This is multi-source BFS. All initially rotten oranges start at time zero, and BFS layers represent minutes.

## Requirements and constraints

- Return `0` if there are no fresh oranges.
- Return `-1` if some fresh orange is unreachable.
- Use four-direction adjacency.
- Prefer `O(rows * cols)` time.

## Recognition cue

Words like "spreads each minute", "simultaneously", and "minimum time" point to BFS from all sources at once.

## Invariant

When a fresh orange is first enqueued, the attached minute is the earliest time it can rot.

## High-level design / approach

1. Scan the grid:
   - enqueue every rotten orange with minute `0`;
   - count fresh oranges.
2. Run BFS.
3. For each popped rotten cell, rot adjacent fresh cells:
   - decrement fresh count;
   - enqueue them with `minute + 1`.
4. If fresh count reaches zero, return the last minute seen.
5. If BFS ends with fresh oranges remaining, return `-1`.

## Dry run

Grid:

```text
2 1 1
1 1 0
0 1 1
```

| Minute | Newly rotten | Fresh left |
|---:|---|---:|
| 0 | `(0,0)` | 6 |
| 1 | `(0,1),(1,0)` | 4 |
| 2 | `(0,2),(1,1)` | 2 |
| 3 | `(2,1)` | 1 |
| 4 | `(2,2)` | 0 |

Answer: `4`.

## Language-neutral pseudocode

```text
queue = all rotten cells with minute 0
fresh = count fresh cells
minutes = 0
while queue is not empty:
    r, c, minute = queue.pop_front()
    minutes = max(minutes, minute)
    for each neighbor:
        if neighbor is fresh:
            mark rotten
            fresh -= 1
            queue.push_back(neighbor, minute + 1)
return minutes if fresh == 0 else -1
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Multi-source setup | Enqueues all initial rotten cells before BFS starts |
| Time model | Ties each BFS level to one minute |
| Unreachable handling | Returns `-1` when fresh remains |
| Complexity | Scans each grid cell a constant number of times |

## Common pitfalls

1. Starting BFS from one rotten orange only.
2. Incrementing minutes per cell instead of per layer or stored time.
3. Returning `1` when no fresh oranges existed.
4. Revisiting cells that are already rotten.

## Follow-up questions

1. How would you handle diagonal spread?
2. How would obstacles or walls change the logic?
3. How would you stream updates if new rotten sources appear later?

## Variants and extensions

- Fire spread in a building grid.
- Infection simulation.
- Queue-based propagation in distributed invalidation.

## Cross-links

- [BFS / DFS Overview](./01-overview.md)
- [Message Queues](../../03-hld-concepts/message-queues/THEORY.md)
