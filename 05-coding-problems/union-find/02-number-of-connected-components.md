# Number of Connected Components

## Overview

Given `n` nodes and undirected edges, return the number of connected components.

Union-Find is a direct fit because each successful union reduces the component count by one.

## Requirements and constraints

- Nodes are usually labeled `0..n-1`.
- Edges are undirected.
- Isolated nodes count as components.
- Duplicate edges should not reduce the count twice.
- Clarify invalid node ids if input is not guaranteed clean.

## Recognition cue

"How many connected components after these undirected edges" is the classic component-counter DSU problem.

## Invariant or state definition

`count` equals the number of distinct roots. A union between two different roots decrements `count`; a union inside the same root does not.

## High-level design / approach

1. Initialize DSU for all `n` nodes.
2. Set `count = n`.
3. For each edge `(u, v)`, call `union(u, v)`.
4. If union returns true, decrement count.
5. Return count.

## Dry run

`n = 5`, edges: `(0,1)`, `(1,2)`, `(3,4)`.

| Edge | Merge? | Components |
|---|---:|---:|
| start | - | 5 |
| `(0,1)` | yes | 4 |
| `(1,2)` | yes | 3 |
| `(3,4)` | yes | 2 |

Components are `{0,1,2}` and `{3,4}`.

## Language-neutral pseudocode

```text
count_components(n, edges):
    dsu = DSU(n)
    count = n
    for u, v in edges:
        if dsu.union(u, v):
            count -= 1
    return count
```

## Complexity proof

Initialization costs `O(n)`. Processing `m` edges costs `O(m * alpha(n))` with path compression and rank. Space is `O(n)`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Initialization | Includes isolated nodes by starting from `n` |
| Merge behavior | Decrements count only on successful union |
| Edge handling | Accepts duplicate edges safely |
| Complexity | Uses `n`, `m`, and near-constant DSU operations |
| Contrast | Can explain BFS/DFS alternative |

## Common pitfalls

1. Counting only nodes that appear in edges.
2. Decrementing for duplicate edges.
3. Using directed graph logic.
4. Forgetting path compression.
5. Returning number of edges left instead of number of roots.

## Follow-up questions

1. How would you list the members of each component?
2. How would BFS/DFS compare?
3. What if edges arrive as a stream and queries happen after each edge?
4. What if edges can be deleted?

## Variants and extensions

- Number of provinces.
- Friend circles.
- Connected components in logs or identity graphs.
- Batch clustering.

## Cross-links

- [Union-Find Overview](./01-overview.md)
- [Number of Provinces](./06-number-of-provinces.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
