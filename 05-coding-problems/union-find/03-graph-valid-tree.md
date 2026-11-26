# Graph Valid Tree

## Overview

Given `n` nodes and undirected edges, decide whether the graph is a valid tree.

A valid tree must be connected and acyclic. For `n` nodes, that means exactly `n - 1` edges and no edge connects nodes already in the same component.

## Requirements and constraints

- Graph is undirected.
- A tree with `n` nodes has exactly `n - 1` edges.
- No cycles are allowed.
- All nodes must be connected.
- Clarify `n = 0` behavior if the prompt allows it.

## Recognition cue

"Valid tree" plus undirected edges signals cycle detection and connectivity. Union-Find can check both with the edge count.

## Invariant or state definition

Before processing an edge, if both endpoints already have the same root, adding that edge creates a cycle.

## High-level design / approach

1. If `len(edges) != n - 1`, return false.
2. Initialize DSU for all nodes.
3. For each edge:
   - if `union(u, v)` returns false, return false because a cycle exists.
4. Return true.

The edge count plus no cycle implies connectivity for an undirected graph.

## Dry run

`n = 5`, edges: `(0,1)`, `(0,2)`, `(0,3)`, `(1,4)`.

There are `4` edges, which equals `n - 1`. Every union succeeds, so the graph is a tree.

If an extra edge `(2,3)` appears, the edge count fails immediately. If edge count were ignored, Union-Find would also detect same-root endpoints.

## Language-neutral pseudocode

```text
valid_tree(n, edges):
    if len(edges) != n - 1:
        return false
    dsu = DSU(n)
    for u, v in edges:
        if not dsu.union(u, v):
            return false
    return true
```

## Complexity proof

The edge-count check is `O(1)`. Processing edges costs `O(m * alpha(n))`; here `m = n - 1` when the check passes. Space is `O(n)`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Tree properties | States connected plus acyclic |
| Edge count | Uses `n - 1` as a fast necessary condition |
| Cycle detection | Fails on same-root edge |
| Connectivity | Explains why edge count plus no cycle is enough |
| Edge cases | Handles single node and duplicate edges |

## Common pitfalls

1. Checking only for no cycle and missing disconnected graphs.
2. Checking only `n - 1` edges and missing cycles with disconnected nodes.
3. Using directed topological logic.
4. Decrementing component count incorrectly.
5. Ignoring duplicate undirected edges.

## Follow-up questions

1. How would BFS/DFS solve this?
2. What changes if the graph is directed?
3. How would you return the cycle edge?
4. How would you validate a forest?

## Variants and extensions

- Redundant connection.
- Minimum spanning tree validation.
- Network topology validation.
- Dependency graph validation, when directed rules apply instead.

## Cross-links

- [Union-Find Overview](./01-overview.md)
- [Redundant Connection](./04-redundant-connection.md)
- [Workflow Orchestration](../../03-hld-concepts/workflow-orchestration/THEORY.md)
