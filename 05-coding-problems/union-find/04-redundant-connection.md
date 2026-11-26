# Redundant Connection

## Overview

Given an undirected graph that started as a tree and then received one extra edge, return the edge that creates a cycle.

Union-Find detects the first edge whose endpoints are already connected.

## Requirements and constraints

- Edges are undirected.
- The graph has one extra edge beyond a tree.
- Return the redundant edge according to input order.
- Node labels may be `1..n`; allocate accordingly or map labels.
- Duplicate edges can also be redundant.

## Recognition cue

"One edge creates a cycle in an undirected graph" is a same-root Union-Find test.

## Invariant or state definition

Before adding an edge, if `find(u) == find(v)`, there is already a path between `u` and `v`; adding the edge closes a cycle.

## High-level design / approach

1. Initialize DSU for all labels.
2. For each edge `(u, v)` in order:
   - if roots are equal, return `(u, v)`;
   - otherwise union the roots.
3. If no edge is redundant, return no result or raise according to prompt.

## Dry run

Edges: `(1,2)`, `(1,3)`, `(2,3)`.

| Edge | Roots before | Action |
|---|---|---|
| `(1,2)` | different | union |
| `(1,3)` | different | union |
| `(2,3)` | same | redundant |

Return `(2,3)`.

## Language-neutral pseudocode

```text
find_redundant(edges):
    dsu = DSU(max_label + 1)
    for u, v in edges:
        if not dsu.union(u, v):
            return [u, v]
    return null
```

## Complexity proof

Processing `m` edges costs `O(m * alpha(n))`. Space is `O(n)` for parent and rank arrays or maps.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Cycle proof | Explains same-root endpoints imply an existing path |
| Input order | Returns the edge when it fails to union |
| Labeling | Handles 1-indexed labels safely |
| Complexity | States near-constant per edge |
| Edge cases | Handles duplicate edge and no-redundant fallback |

## Common pitfalls

1. Returning the first edge after a node repeats.
2. Forgetting labels may start at `1`.
3. Unioning before checking roots and losing the signal.
4. Applying directed-cycle logic to an undirected prompt.
5. Returning all cycle edges instead of the requested redundant one.

## Follow-up questions

1. How would the directed version differ?
2. How would you return the full cycle path?
3. How would this work in a streaming network monitor?
4. How would you handle multiple redundant edges?

## Variants and extensions

- Graph valid tree.
- Network loop detection.
- Duplicate relationship detection.
- Incremental topology validation.

## Cross-links

- [Graph Valid Tree](./03-graph-valid-tree.md)
- [Union-Find Overview](./01-overview.md)
- [LinkedIn Connection LLD](../../02-lld-projects/linkedin-connection/)
