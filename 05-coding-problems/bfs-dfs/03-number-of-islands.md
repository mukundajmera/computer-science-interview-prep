# Number of Islands

## Overview

Given a grid of `1` land and `0` water, count connected groups of land. Cells connect horizontally and vertically.

This is connected-component traversal on an implicit graph: each land cell is a node, and its four adjacent land cells are neighbors.

## Requirements and constraints

- Count each island once.
- Use four-direction adjacency unless the prompt explicitly allows diagonals.
- State whether mutating the grid is allowed.
- Prefer `O(rows * cols)` time.

## Recognition cue

"Count regions", "connected land", and "grid components" all point to flood fill using DFS or BFS.

## Invariant

After a traversal starts from an unvisited land cell, every land cell in that island is marked visited before the island count moves on.

## High-level design / approach

1. Initialize `count = 0`.
2. Scan every cell.
3. When an unvisited land cell is found:
   - increment `count`;
   - flood-fill from that cell using DFS or BFS;
   - mark all reachable land visited.
4. Return `count`.

## Dry run

Grid:

```text
1 1 0
0 1 0
1 0 1
```

| Scan cell | Action | Count |
|---|---|---:|
| `(0,0)` | new island; visits `(0,0),(0,1),(1,1)` | 1 |
| `(2,0)` | new island; isolated | 2 |
| `(2,2)` | new island; isolated | 3 |

## Language-neutral pseudocode

```text
count = 0
for r in rows:
    for c in cols:
        if grid[r][c] is land and not visited:
            count += 1
            traverse(r, c)

traverse(r, c):
    if out of bounds or water or visited:
        return
    mark visited
    for each of four directions:
        traverse(next_r, next_c)
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Graph model | Treats land cells as nodes and four-neighbor links as edges |
| Count timing | Increments only when discovering a new component root |
| Visited handling | Marks before recursing or enqueueing neighbors |
| Complexity | `O(rows * cols)` time and `O(rows * cols)` worst-case space |

## Common pitfalls

1. Counting every land cell instead of every component.
2. Including diagonal neighbors by accident.
3. Mutating the grid without saying so.
4. Recursing deeply on a huge grid without considering iterative BFS/DFS.

## Follow-up questions

1. How would you return island sizes?
2. How would you count islands in a stream of land additions?
3. How would you distribute this over sharded map tiles?

## Variants and extensions

- Max area of island.
- Surrounded regions.
- Dynamic island count with union-find.

## Cross-links

- [BFS / DFS Overview](./01-overview.md)
