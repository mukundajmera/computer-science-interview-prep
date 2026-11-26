# Union-Find Overview

## Overview

Union-Find maintains a partition of items into disjoint sets. Each set has a representative root.

The core model is simple:

```text
parent[x] = current parent pointer
rank_or_size[x] = approximate tree height or component size
find(x) = representative root
union(a, b) = merge two different roots
```

## Requirements and constraints

- Define the item universe: `0..n-1`, strings, emails, rows, columns, or lazily discovered ids.
- Decide whether you need component count, component size, or just connectivity.
- Use path compression in `find`.
- Use union by rank or size.
- Clarify whether edges are undirected and only added.

## Recognition cue

The strongest cue is repeated merging: "same group", "same component", "connected after edges", "merge identities", or "detect if this undirected edge closes a cycle."

## Invariant or state definition

Two items are in the same component if and only if `find(a) == find(b)`. Parent pointers may change over time, but roots represent current groups.

## High-level design / approach

1. Initialize each item as its own parent.
2. `find(x)` follows parent pointers to the root.
3. Path compression rewrites visited nodes directly to the root.
4. `union(a, b)` finds roots.
5. If roots differ, link one root under the other using rank or size.
6. Update component count or size only when roots differ.

## Dry run

Items: `0, 1, 2, 3`.

| Operation | Result | Component count |
|---|---|---:|
| start | `{0}`, `{1}`, `{2}`, `{3}` | 4 |
| union(0, 1) | `{0,1}`, `{2}`, `{3}` | 3 |
| union(2, 3) | `{0,1}`, `{2,3}` | 2 |
| union(1, 3) | `{0,1,2,3}` | 1 |
| union(0, 2) | already connected | 1 |

The last union does not decrement the count.

## Language-neutral pseudocode

```text
find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

union(a, b):
    root_a = find(a)
    root_b = find(b)
    if root_a == root_b:
        return false
    if rank[root_a] < rank[root_b]:
        parent[root_a] = root_b
    else if rank[root_a] > rank[root_b]:
        parent[root_b] = root_a
    else:
        parent[root_b] = root_a
        rank[root_a] += 1
    return true
```

## Complexity proof

With path compression and union by rank or size, `find` and `union` are near-constant amortized time, commonly written as `O(alpha(n))`, where `alpha` grows so slowly it is effectively constant for interview input sizes. Space is `O(n)`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| API | Implements `find` and `union` cleanly |
| Compression | Updates parent pointers during `find` |
| Rank/size | Avoids tall trees |
| Count updates | Changes counts only on successful union |
| Limits | States Union-Find does not return paths |

## Common pitfalls

1. Returning parent without chasing to the root.
2. Forgetting to compress paths.
3. Incrementing rank on every union instead of only equal-rank merges.
4. Decrementing component count on a duplicate edge.
5. Creating ids only for items that appear in edges and missing isolated nodes.

## Follow-up questions

1. How would you track component sizes?
2. How would you map string ids to integer ids?
3. How would online edge deletion change the problem?
4. How would you expose connected-component membership?

## Variants and extensions

- DSU with size.
- DSU over strings or emails.
- DSU over row and column ids.
- Rollback DSU for offline dynamic connectivity.

## Cross-links

- [Union-Find Pattern Pack](./README.md)
- [Number of Connected Components](./02-number-of-connected-components.md)
- [BFS/DFS Pattern Pack](../bfs-dfs/README.md)
