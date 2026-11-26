# Coach Answer: Coding Union-Find Pack

> Type: Coding Pattern Drill
> Difficulty: Intermediate
> Time Target: 45 minutes

## Phase 1 - Problem Framing

Strong candidates do not say "use DSU" and stop. They define the component model.

1. Identify items: nodes, emails, variables, rows, columns, or accounts.
2. Define why relationships are undirected equivalence relationships.
3. Map non-integer keys to stable ids.
4. Define `parent`, `rank` or `size`, `find`, and `union`.
5. State the invariant: same root means same component.
6. Update counts or sizes only when roots differ.
7. Reject DSU when the prompt needs paths, directed reachability, shortest path, or online deletion.

## Phase 2 - Canonical Templates

### Template A: DSU Core

```text
find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

union(a, b):
    ra = find(a)
    rb = find(b)
    if ra == rb: return false
    attach lower-rank root under higher-rank root
    return true
```

Use for every DSU problem before specializing.

### Template B: Component Counter

```text
count = n
for edge in edges:
    if union(edge.u, edge.v):
        count -= 1
return count
```

Use when successful merges reduce groups.

### Template C: Cycle Detector

```text
for edge in edges:
    if find(edge.u) == find(edge.v):
        return edge
    union(edge.u, edge.v)
```

Use for undirected redundant edges and valid-tree cycle checks.

### Template D: String-Key Merger

```text
id = get_or_create_id(key)
union(keys that belong together)
groups[find(id)].append(key)
```

Use for accounts, identities, aliases, and duplicate clusters.

## Phase 3 - Problem-by-Problem Walkthrough

1. **Number of Connected Components**
   - State: `count = n`.
   - Successful union decrements count.

2. **Graph Valid Tree**
   - State: edge count plus DSU cycle check.
   - Need exactly `n - 1` edges and no failed union.

3. **Redundant Connection**
   - State: process edges in order.
   - First failed union is the redundant edge.

4. **Accounts Merge**
   - State: email-to-id map and email groups by final root.
   - Merge by shared email, not display name.

5. **Number of Provinces**
   - State: city components from matrix entries.
   - Matrix scan dominates runtime.

6. **Most Stones Removed**
   - State: row nodes and column nodes in the same DSU.
   - Answer is stones minus connected components.

7. **Satisfiability of Equality Equations**
   - State: equality classes.
   - Process equality first; then reject same-root inequality.

## Phase 4 - Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Model fit | 20% | Explains why the relation is undirected equivalence |
| DSU implementation | 20% | Uses path compression and rank or size |
| Invariant | 20% | Same root means same component |
| Count/group updates | 15% | Updates only on successful merge and groups by final root |
| Edge cases | 15% | Handles duplicates, isolated nodes, string ids, and invalid assumptions |
| Limits | 10% | Rejects DSU for paths, directed reachability, and online deletion |

## Phase 5 - Common Pitfalls

1. Missing isolated nodes.
2. Decrementing count on duplicate edges.
3. Comparing raw parents instead of `find` results.
4. Merging accounts by name.
5. Colliding row and column ids.
6. Processing inequalities before equalities.
7. Using DSU for directed reachability.
8. Claiming DSU returns paths.

## System Design Transfer Script

| DSU concept | Production analogue | Scale risk | Validation signal |
|---|---|---|---|
| Component root | identity cluster id | false merge blast radius | sampled merge precision |
| Union evidence | shared email, device, account, edge | weak or spoofed evidence | evidence audit coverage |
| Component count | number of clusters | missed merges | recall estimate |
| String id map | user/device/email id mapping | inconsistent keys | mapping error rate |
| Rollback DSU idea | reversible merge workflow | irreversible bad merge | rollback success and audit trail |

## Follow-Up Drill Set

1. Number of Connected Components.
2. Graph Valid Tree.
3. Redundant Connection.
4. Accounts Merge.
5. Number of Provinces.
6. Most Stones Removed.
7. Satisfiability of Equality Equations.
8. Identity merge service design.

## Cross-links

- [Union-Find Pattern Pack](../05-coding-problems/union-find/README.md)
- [Union-Find Quiz](../quizzes/union-find-quiz.md)
- [Union-Find Flashcards](../flashcards/union-find.md)
- [BFS/DFS Pattern Pack](../05-coding-problems/bfs-dfs/README.md)
- [Distributed Coordination](../03-hld-concepts/distributed-coordination/THEORY.md)
