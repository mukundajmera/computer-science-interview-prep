# BFS / DFS Overview

## Overview

BFS and DFS solve graph-shaped problems by making exploration explicit. The input may look like a tree, grid, list of prerequisites, adjacency list, word transformations, or state machine. Your first job is to define the graph without overbuilding it.

Use this sequence before coding:

1. Identify nodes.
2. Define neighbors.
3. Decide whether the graph is directed or undirected.
4. Decide what "visited" means.
5. Choose BFS for shortest unweighted distance or layers; choose DFS for exhaustive component/path/cycle reasoning.

## Requirements and constraints

- Every reachable node should be processed at most once unless the state definition intentionally includes more dimensions.
- For graph inputs, account for `V` nodes and `E` edges.
- For grids, account for `rows * cols` cells and neighbor directions.
- For trees, account for height or maximum level width in auxiliary space.
- For directed dependency graphs, separate visited-complete nodes from nodes currently in the active recursion stack.

## High-level design / approach

| Question | BFS answer | DFS answer |
|---|---|---|
| What is the frontier? | Queue of next nodes by distance/layer | Call stack or explicit stack of the current path |
| When mark visited? | Usually before enqueue | On entry, with optional color state |
| Best interview signal | Shortest unweighted path, level order, spreading | Components, cycle detection, postorder, backtracking-like exploration |
| Space risk | Wide frontier | Deep recursion stack |

## Dry run

Graph edges: `A-B`, `A-C`, `B-D`, `C-E`. Start at `A`.

| Step | BFS queue | Visited | Output |
|---:|---|---|---|
| 0 | `[A]` | `{A}` | `[]` |
| 1 | `[B, C]` | `{A, B, C}` | `[A]` |
| 2 | `[C, D]` | `{A, B, C, D}` | `[A, B]` |
| 3 | `[D, E]` | `{A, B, C, D, E}` | `[A, B, C]` |
| 4 | `[E]` | `{A, B, C, D, E}` | `[A, B, C, D]` |
| 5 | `[]` | `{A, B, C, D, E}` | `[A, B, C, D, E]` |

DFS from `A` might output `A, B, D, C, E` depending on neighbor order. Both are valid traversals, but only BFS preserves increasing distance from `A`.

## Language-neutral pseudocode

```text
bfs(start):
    queue = [start]
    visited = {start}
    while queue is not empty:
        node = queue.pop_front()
        for next in neighbors(node):
            if next not in visited:
                visited.add(next)
                queue.push_back(next)

dfs(node):
    mark node visited
    for next in neighbors(node):
        if next not visited:
            dfs(next)
```

## Scoring rubric

| Dimension | What interviewers look for |
|---|---|
| Modeling | Clear node, edge, and neighbor definition |
| Traversal choice | Correctly chooses BFS or DFS for the prompt |
| Visited discipline | Prevents cycles and duplicate work |
| Disconnected handling | Loops over all nodes when one start is not enough |
| Complexity | States `O(V + E)` or `O(rows * cols)` with real auxiliary space |

## Common pitfalls

1. Confusing traversal order with correctness.
2. Forgetting to include the starting node in `visited`.
3. Treating recursive DFS stack as free.
4. Using one global visited set when the state should include `(node, depth)` or `(node, remaining_resource)`.

## Follow-up questions

1. When would bidirectional BFS help?
2. How do you avoid recursion limits?
3. What changes when the graph is too large for one machine?
4. How do you handle weighted edges?

## Variants and extensions

- Bidirectional BFS for shortest transformations.
- Iterative DFS with an explicit stack.
- Kahn's algorithm for topological ordering.
- Multi-source BFS for simultaneous spread.

## Cross-links

- [BFS / DFS Pattern Pack](./README.md)
- [Course Schedule](./06-course-schedule.md)
- [Word Ladder](./07-word-ladder.md)
- [Web Crawler HLD](../../04-hld-projects/web-crawler/)
