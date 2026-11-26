# Most Stones Removed

## Overview

Given stones on a 2D grid, remove as many stones as possible where a stone can be removed if another stone remains in the same row or column.

The insight: stones connected by shared rows or columns form components. In each component with `k` stones, you can remove `k - 1` stones, leaving one anchor.

## Requirements and constraints

- Stones share an edge relationship when row or column matches.
- Return maximum removable stones.
- Avoid pairwise comparison when possible.
- Rows and columns must not collide if encoded in one DSU.
- Coordinate values may be large.

## Recognition cue

"Same row or same column" creates connectivity. "Remove all but one per component" is a component-count formula.

## Invariant or state definition

Every row id and column id connected by a stone belongs to that stone's component. The answer is `stones_count - number_of_components_with_stones`.

## High-level design / approach

1. Treat each row and each column as nodes in a DSU universe.
2. For each stone `(r, c)`, union row node `r` with column node `c`.
3. Track every row/column node that appears.
4. Count distinct roots among appeared nodes.
5. Return `len(stones) - component_count`.

## Dry run

Stones: `(0,0)`, `(0,1)`, `(1,0)`, `(2,2)`.

Rows `r0`, `r1` and columns `c0`, `c1` form one component through the first three stones. Row `r2` and column `c2` form a second component. With 4 stones and 2 components, answer is `2`.

## Language-neutral pseudocode

```text
for r, c in stones:
    row_id = encode_row(r)
    col_id = encode_col(c)
    dsu.add(row_id)
    dsu.add(col_id)
    dsu.union(row_id, col_id)
    seen.add(row_id)
    seen.add(col_id)

roots = set(dsu.find(x) for x in seen)
return len(stones) - len(roots)
```

## Complexity proof

For `s` stones, DSU operations cost `O(s * alpha(s))` after id mapping. Space is `O(s)` because only rows and columns that appear need nodes.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Modeling | Converts row/column sharing into DSU connectivity |
| Id safety | Prevents row and column id collisions |
| Formula | Uses stones minus connected components |
| Scale | Avoids `O(s^2)` pairwise checks |
| Edge cases | Handles one stone and isolated components |

## Common pitfalls

1. Unioning stones pairwise in `O(s^2)` without need.
2. Colliding row id `1` with column id `1`.
3. Counting roots over all possible coordinates instead of seen nodes.
4. Returning component count instead of removable count.
5. Assuming one component can remove every stone.

## Follow-up questions

1. Why does each component leave one stone?
2. How would pairwise stone DSU compare?
3. How would you encode negative coordinates?
4. What if removals had costs or priorities?

## Variants and extensions

- Bipartite row-column grouping.
- Sparse grid connectivity.
- Duplicate coordinate detection.
- Batch clustering over shared attributes.

## Cross-links

- [Union-Find Overview](./01-overview.md)
- [Number of Connected Components](./02-number-of-connected-components.md)
- [Pattern to System Design Map](../PATTERN-SD-MAP.md)
