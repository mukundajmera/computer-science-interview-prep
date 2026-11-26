# Pacific Atlantic Water Flow

## Overview

Given a height grid, return cells from which water can flow to both the Pacific and Atlantic oceans. Water can flow from a cell to neighboring cells with height less than or equal to the current cell.

The trick is reversing the search. Instead of starting from every cell and asking whether it can reach both oceans, start from each ocean boundary and move uphill. Cells reached by both reverse searches are the answer.

## Requirements and constraints

- Use four-direction adjacency.
- Return all coordinates that can reach both oceans.
- Avoid running a full traversal from every cell.
- Prefer `O(rows * cols)` time.

## Recognition cue

"Can reach boundary", "both sinks", and "many sources" suggest reverse reachability from the sinks.

## Invariant

In the reversed search, a cell is marked reachable from an ocean if water from that cell can flow downhill to that ocean in the original direction.

## High-level design / approach

1. Create two visited sets: `pacific_reachable` and `atlantic_reachable`.
2. Start DFS or BFS from all Pacific-border cells and move only to neighbors with height greater than or equal to current height.
3. Do the same from all Atlantic-border cells.
4. Return the intersection of the two reachable sets.

## Dry run

For a small grid:

```text
1 2 2
3 2 3
2 4 5
```

Pacific reverse search starts from top row and left column. Atlantic reverse search starts from bottom row and right column. A cell like `(1,2)` with height `3` can be reached from both reverse searches, so in the original direction it can flow to both oceans.

| Stage | Reachable coordinates | Why |
|---|---|---|
| Pacific starts | top row `(0,0..2)`, left column `(0..2,0)` | These cells already touch the Pacific boundary. |
| Pacific uphill expansion | adds `(1,1)`, `(1,2)`, `(2,1)`, `(2,2)` | Each added cell is at least as high as the cell that reached it, so it can flow back downhill to the Pacific. |
| Atlantic starts | bottom row `(2,0..2)`, right column `(0..2,2)` | These cells already touch the Atlantic boundary. |
| Atlantic uphill expansion | adds `(1,2)`, `(2,1)`, `(2,2)` | Lower cells cannot climb back to higher cells in the reversed search. |
| Intersection | `(1,2)`, `(2,1)`, `(2,2)` | These are reachable from both reverse searches, so they can flow to both oceans in the original direction. |

## Language-neutral pseudocode

```text
search(starts):
    visited = set(starts)
    stack_or_queue = starts
    while stack_or_queue not empty:
        cell = pop()
        for neighbor in four directions:
            if in bounds and neighbor not visited:
                if height[neighbor] >= height[cell]:
                    visited.add(neighbor)
                    push(neighbor)
    return visited

pacific = search(top row + left column)
atlantic = search(bottom row + right column)
return cells in pacific intersection atlantic
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Direction reversal | Explains why moving uphill from oceans is equivalent |
| Boundary starts | Uses all border cells for each ocean |
| Intersection | Returns cells reachable from both searches |
| Complexity | Each ocean search visits each cell at most once |

## Common pitfalls

1. Starting DFS from every cell and timing out.
2. Using the original downhill comparison during reverse search.
3. Missing one of the border rows or columns.
4. Duplicating border cells without visited protection.

## Follow-up questions

1. How would diagonal flow change the neighbor function?
2. How would you handle streaming height updates without recomputing both full searches on every write?
3. How would you shard the grid if it is too large for one machine?

## Variants and extensions

- Surrounded regions via boundary reverse search.
- Multi-sink reachability.
- Data-flow analysis from terminal states.

## Cross-links

- [BFS / DFS Overview](./01-overview.md)
- [Number of Islands](./03-number-of-islands.md)
- [Web Crawler HLD](../../04-hld-projects/web-crawler/)
