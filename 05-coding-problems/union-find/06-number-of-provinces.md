# Number of Provinces

## Overview

Given an adjacency matrix where `isConnected[i][j]` indicates a direct connection between cities, return the number of provinces.

This is connected components over an undirected graph represented as a matrix.

## Requirements and constraints

- Matrix is usually square `n x n`.
- Connections are undirected and symmetric.
- A city is connected to itself.
- Isolated cities count as provinces.
- Avoid double-processing if scanning the full matrix.

## Recognition cue

"Number of provinces" is connected components with matrix input instead of edge-list input.

## Invariant or state definition

Each successful union between two different city roots reduces the province count by one.

## High-level design / approach

1. Initialize DSU for `n` cities and `count = n`.
2. Scan only one triangle of the matrix, such as `j > i`.
3. When `isConnected[i][j] == 1`, union `i` and `j`.
4. Decrement count on successful union.
5. Return count.

## Dry run

Matrix:

```text
1 1 0
1 1 0
0 0 1
```

Cities `0` and `1` merge. City `2` stays isolated. Answer is `2`.

## Language-neutral pseudocode

```text
find_circle_num(matrix):
    n = len(matrix)
    dsu = DSU(n)
    count = n
    for i in range(0, n):
        for j in range(i + 1, n):
            if matrix[i][j] == 1 and dsu.union(i, j):
                count -= 1
    return count
```

## Complexity proof

Scanning the matrix costs `O(n^2)`. DSU operations are near-constant amortized. Space is `O(n)`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Matrix handling | Scans valid pairs without missing edges |
| Components | Counts isolated cities |
| DSU updates | Decrements only on successful union |
| Complexity | States matrix scan dominates |
| Alternative | Can describe DFS over matrix rows |

## Common pitfalls

1. Counting direct friendships rather than components.
2. Scanning both triangles and decrementing twice.
3. Ignoring isolated cities.
4. Treating the matrix as directed.
5. Returning the number of roots without compressing or grouping correctly.

## Follow-up questions

1. How would an edge-list input change the solution?
2. How would DFS compare for this matrix?
3. What if matrix entries update online?
4. How would you handle millions of sparse cities?

## Variants and extensions

- Friend circles.
- Region clusters.
- Service dependency groups.
- Sparse graph connected components.

## Cross-links

- [Number of Connected Components](./02-number-of-connected-components.md)
- [BFS/DFS Pattern Pack](../bfs-dfs/README.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
