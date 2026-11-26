# Union-Find Pattern Pack

A focused coding pattern pack for dynamic connectivity and grouping problems: connected components, valid trees, redundant edges, account merging, provinces, removable stones, and equality constraints.

## Overview

Union-Find, also called Disjoint Set Union, tracks which items belong to the same component. It supports two core operations:

1. `find(x)`: return the representative parent of `x`.
2. `union(a, b)`: merge the components containing `a` and `b`.

Use it when the problem processes relationships and repeatedly asks whether two items are already connected or how many groups remain. The interview signal is path compression, union by rank or size, and knowing when Union-Find is the wrong tool for online path queries.

## When to Use

Use Union-Find when the prompt gives you:

1. Undirected connectivity.
2. Component counting while edges are added.
3. Duplicate grouping or identity merge.
4. Cycle detection in an undirected graph.
5. Equivalence constraints such as `a == b`.

Strong recognition cues:

- "connected components"
- "are these nodes connected?"
- "merge accounts"
- "valid tree"
- "redundant connection"
- "number of provinces"
- "remove stones sharing row or column"
- "satisfiability of equality equations"

## When Not to Use

Avoid Union-Find when:

1. You need the actual path between two nodes.
2. Edges are removed online and queries must reflect deletion immediately.
3. The graph is directed and reachability direction matters.
4. You need shortest path, topological order, or traversal sequence.
5. The relationship changes require transactional history or time-travel queries.

The common warning: Union-Find is excellent for component identity, not for exploring graph structure.

## Pattern Taxonomy

| Variant | Best fit | Key invariant |
|---|---|---|
| Component counter | connected components, provinces | decrement count only when two different roots merge |
| Cycle detector | valid tree, redundant connection | an edge inside the same component creates an undirected cycle |
| Attribute merger | accounts merge | emails or ids point to one representative group |
| Row/column grouping | stones removed | row and column ids become nodes in one DSU universe |
| Equality constraints | equations possible | process equality first, contradiction on inequality with same root |
| Union by size | group-size queries | root stores component size |
| Path compression | performance | every find shortens future paths |

## Common Failure Modes

1. Forgetting path compression and creating tall parent chains.
2. Decrementing component count even when nodes are already connected.
3. Applying Union-Find to directed reachability.
4. Missing isolated nodes that never appear in an edge list.
5. Failing to map strings, emails, rows, or columns into stable ids.
6. Treating valid tree as "no cycle" but forgetting `edges == n - 1`.
7. Processing inequalities before equalities in satisfiability problems.
8. Colliding row and column ids in stone-removal problems.

## Interview Scoring Focus

| Dimension | Strong signal |
|---|---|
| DSU API | Defines parent, rank or size, `find`, and `union` |
| Correctness | Explains root equality as same component |
| Count updates | Decrements groups only on successful merge |
| Mapping | Handles non-integer keys safely |
| Complexity | States near-constant amortized time with path compression and rank |
| Limits | Knows when traversal, directed graph logic, or deletion needs another structure |

## 60-90 Second Answer

Say:

"I use Union-Find when relationships form undirected components and the question is whether items are in the same group or how many groups remain. Each item starts as its own parent. `find` returns the root representative and compresses the path. `union` compares roots and links the smaller rank or size under the larger root; if the roots were different, one component disappears. That makes edge processing almost constant amortized time. I would not use Union-Find when the interviewer asks for the actual path, directed reachability, shortest path, or online edge deletion."

## Problem Track

1. [01-overview.md](./01-overview.md)
2. [02-number-of-connected-components.md](./02-number-of-connected-components.md)
3. [03-graph-valid-tree.md](./03-graph-valid-tree.md)
4. [04-redundant-connection.md](./04-redundant-connection.md)
5. [05-accounts-merge.md](./05-accounts-merge.md)
6. [06-number-of-provinces.md](./06-number-of-provinces.md)
7. [07-most-stones-removed.md](./07-most-stones-removed.md)
8. [08-satisfiability-of-equality-equations.md](./08-satisfiability-of-equality-equations.md)

## Cross-links

- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
- [Pattern to System Design Map](../PATTERN-SD-MAP.md)
- [BFS/DFS Pattern Pack](../bfs-dfs/README.md)
- [LinkedIn Connection LLD](../../02-lld-projects/linkedin-connection/)
- [Distributed Coordination](../../03-hld-concepts/distributed-coordination/THEORY.md)
- [Bot Detection Platform](../../04-hld-projects/bot-detection-platform/)
- [Union-Find Quiz](../../quizzes/union-find-quiz.md)
- [Union-Find Flashcards](../../flashcards/union-find.md)
- [Coach Answer: Coding Union-Find](../../solutions/coding-union-find.md)
