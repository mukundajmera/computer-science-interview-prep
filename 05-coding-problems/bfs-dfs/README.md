# BFS / DFS Pattern Pack

A focused coding pattern pack for tree traversal, graph reachability, grid flood fill, shortest paths in unweighted graphs, connected components, and dependency ordering.

## Overview

BFS and DFS are not just "visit nodes." They are ways to control exploration.

- BFS explores by distance or layer. Use it when the first time you reach a node is meaningful, such as shortest path in an unweighted graph.
- DFS explores one path deeply before backtracking. Use it when you need to exhaust a component, detect cycles, or build postorder structure.

The core contract is: define neighbors, define what counts as visited, and decide when a node becomes visited. Most interview bugs come from marking visited too late, ignoring disconnected components, or using DFS where level order matters.

## When to Use

Use BFS/DFS when the problem gives you:

1. Nodes and edges, explicitly or implicitly.
2. A grid where each cell can connect to adjacent cells.
3. A tree traversal problem.
4. Reachability, connected components, shortest unweighted distance, cycle detection, or dependency ordering.
5. A state-space search where each state has valid next states.

Strong recognition cues:

- "nearest", "minimum number of steps", "level order", "spread over minutes"
- "island", "region", "component", "connected"
- "can finish all courses", "dependencies", "cycle"
- "clone graph", "visited set", "avoid revisiting"
- "all paths", "reach both oceans", "boundary expansion"

## When Not to Use

Avoid plain BFS/DFS when:

1. Edge weights matter. Use Dijkstra or another weighted shortest-path algorithm.
2. The graph is too large for an unbounded visited set and the prompt expects a bounded or bidirectional search.
3. The problem is really ordering by priority, not reachability.
4. You only need membership lookup, not traversal.
5. Recursive DFS would exceed stack depth and the interviewer expects an iterative approach.

## Pattern Taxonomy

| Variant | Best fit | Key invariant |
|---|---|---|
| Tree DFS | depth, path, subtree questions | current recursion frame represents the path from root |
| Tree BFS | level order, nearest leaf | queue contains the current frontier by depth |
| Grid flood fill | islands, regions, boundaries | visited land cells are counted once |
| Graph BFS | shortest unweighted path | first discovery gives minimum edge distance |
| Graph DFS | components, cycle detection | recursion stack or color state identifies active path |
| Topological traversal | dependency ordering | nodes leave the queue only after prerequisites are satisfied |
| Multi-source BFS | spreading processes | all starting points begin at distance or time zero |
| Boundary reverse search | reachability to borders/sinks | search from sinks can be cheaper than trying every source |

## Common Failure Modes

1. Marking visited after dequeue instead of before enqueue and allowing duplicate queue growth.
2. Forgetting disconnected components.
3. Using DFS for shortest unweighted distance when BFS is required.
4. Missing directed-cycle handling in dependency graphs.
5. Counting BFS levels off by one.
6. Mutating a grid without confirming that input mutation is allowed.
7. Claiming DFS is `O(1)` space while recursion uses stack frames.
8. Rebuilding neighbors inefficiently for every node when preprocessing would be clearer.

## Interview Scoring Focus

| Dimension | Strong signal |
|---|---|
| Graph modeling | Converts grid/tree/dependencies into nodes and neighbors |
| Visited timing | Marks at discovery for BFS or with clear color states for DFS |
| Traversal choice | Explains BFS vs DFS instead of treating them as interchangeable |
| Component coverage | Handles disconnected graphs and all starting points |
| Complexity honesty | Counts nodes, edges, queue/frontier, visited set, and recursion stack |
| Follow-up depth | Can discuss bidirectional BFS, iterative DFS, topological sort, and memory limits |

## 60-90 Second Answer

Say:

"I first model the input as nodes with neighbors. If the prompt asks for nearest distance or level-by-level spread, I use BFS because the queue expands by edge count and the first time I discover a node is the shortest unweighted path. If the prompt asks for exhausting a region, detecting a cycle, or exploring all nodes in a component, I use DFS with a visited set or color states. The invariant is that every node is processed at most once, and every edge is inspected only when exploring a node. I will mark nodes at discovery to avoid duplicate work, handle disconnected components by looping over all nodes when needed, and state space as `O(V + E)` for visited plus queue or recursion stack."

## Problem Track

1. [01-overview.md](./01-overview.md)
2. [02-binary-tree-level-order-traversal.md](./02-binary-tree-level-order-traversal.md)
3. [03-number-of-islands.md](./03-number-of-islands.md)
4. [04-clone-graph.md](./04-clone-graph.md)
5. [05-rotting-oranges.md](./05-rotting-oranges.md)
6. [06-course-schedule.md](./06-course-schedule.md)
7. [07-word-ladder.md](./07-word-ladder.md)
8. [08-pacific-atlantic-water-flow.md](./08-pacific-atlantic-water-flow.md)

## Cross-links

- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
- [Pattern to System Design Map](../PATTERN-SD-MAP.md)
- [Web Crawler HLD](../../04-hld-projects/web-crawler/)
- [Workflow Orchestration](../../03-hld-concepts/workflow-orchestration/THEORY.md)
- [LinkedIn Connection LLD](../../02-lld-projects/linkedin-connection/)
- [BFS/DFS Quiz](../../quizzes/bfs-dfs-quiz.md)
- [BFS/DFS Flashcards](../../flashcards/bfs-dfs.md)
- [Coach Answer: Coding BFS/DFS](../../solutions/coding-bfs-dfs.md)
