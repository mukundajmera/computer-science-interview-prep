# Clone Graph

## Overview

Given a reference to a node in an undirected graph, create a deep copy of the entire reachable graph.

The key idea is not traversal alone; it is preserving identity. Each original node must map to exactly one cloned node so cycles and shared neighbors remain correct.

## Requirements and constraints

- Return `null` for `null` input.
- Clone all reachable nodes.
- Preserve neighbor relationships.
- Do not create duplicate clones for the same original node.

## Recognition cue

"Deep copy graph" plus "cycles" or "neighbors" signals traversal with an original-to-clone map.

## Invariant

For every original node already seen, `clone_map[original]` points to the single clone that all later edges must reuse.

## High-level design / approach

1. If input node is null, return null.
2. Create a map from original node to clone node.
3. Traverse the graph with DFS or BFS.
4. When visiting an original neighbor:
   - create its clone if missing;
   - append the neighbor clone to the current clone's neighbor list.
5. Return the clone mapped from the input node.

## Dry run

Graph: `1 -- 2`, `1 -- 3`, `2 -- 3`.

| Visit | Clone action | Edge action |
|---|---|---|
| `1` | create clone `1'` | prepare neighbors |
| `2` from `1` | create clone `2'` | add `2'` to `1'` |
| `3` from `1` | create clone `3'` | add `3'` to `1'` |
| `3` from `2` | reuse clone `3'` | add `3'` to `2'` |

No duplicate clone of `3` is created.

## Language-neutral pseudocode

```text
if node is null:
    return null
clone_map[node] = new Node(node.value)
queue = [node]
while queue is not empty:
    original = queue.pop_front()
    for neighbor in original.neighbors:
        if neighbor not in clone_map:
            clone_map[neighbor] = new Node(neighbor.value)
            queue.push_back(neighbor)
        clone_map[original].neighbors.append(clone_map[neighbor])
return clone_map[node]
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Identity map | Uses original node object/reference as the key |
| Cycle safety | Does not recursively copy forever |
| Edge preservation | Rebuilds neighbor links between cloned nodes only |
| Complexity | `O(V + E)` time, `O(V)` clone map plus traversal storage |

## Common pitfalls

1. Keying the map only by value when values are not guaranteed unique.
2. Adding original neighbors to cloned nodes.
3. Creating clones lazily but forgetting to traverse them.
4. Using no map and duplicating shared nodes.

## Follow-up questions

1. What changes for directed graphs?
2. How would you clone only nodes within distance `k`?
3. How would you preserve extra metadata on edges?

## Variants and extensions

- Copy random-pointer linked list.
- Snapshot a workflow graph.
- Clone a dependency graph for simulation.

## Cross-links

- [BFS / DFS Overview](./01-overview.md)
- [Workflow Orchestration](../../03-hld-concepts/workflow-orchestration/THEORY.md)
