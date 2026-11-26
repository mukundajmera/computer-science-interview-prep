# Binary Tree Level Order Traversal

## Overview

Given a binary tree, return node values level by level from top to bottom. This is the cleanest BFS tree problem because each queue cycle corresponds to one depth level.

## Requirements and constraints

- Return an empty list for an empty tree.
- Preserve left-to-right order within each level.
- Prefer `O(n)` time.
- Auxiliary space is `O(w)`, where `w` is maximum tree width.

## Recognition cue

The phrase "level order" is a direct BFS signal. DFS can group by depth, but BFS is simpler because the queue already preserves layers.

## Invariant

At the start of each outer loop, the queue contains exactly the nodes for the next output level.

## High-level design / approach

1. If root is null, return `[]`.
2. Push root into a queue.
3. While the queue is not empty:
   - capture current queue size;
   - process exactly that many nodes into one level list;
   - enqueue each processed node's children.
4. Append the level list to the answer.

## Dry run

Tree: `3` with children `9` and `20`; `20` has children `15` and `7`.

| Iteration | Queue at level start | Output level | Queue after level |
|---:|---|---|---|
| 1 | `[3]` | `[3]` | `[9, 20]` |
| 2 | `[9, 20]` | `[9, 20]` | `[15, 7]` |
| 3 | `[15, 7]` | `[15, 7]` | `[]` |

Answer: `[[3], [9, 20], [15, 7]]`.

## Language-neutral pseudocode

```text
if root is null:
    return []
queue = [root]
answer = []
while queue is not empty:
    level_size = queue.size()
    level = []
    repeat level_size times:
        node = queue.pop_front()
        level.append(node.value)
        if node.left: queue.push_back(node.left)
        if node.right: queue.push_back(node.right)
    answer.append(level)
return answer
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Level boundary | Captures queue size before processing the level |
| Order | Enqueues left child before right child |
| Empty input | Returns `[]` without special failures |
| Complexity | Uses `O(n)` time and `O(w)` queue space |

## Common pitfalls

1. Looping until queue empty inside one level and merging all levels.
2. Appending children to the same level list.
3. Claiming `O(1)` space because the output is ignored but the queue is not.

## Follow-up questions

1. How would you return zigzag level order?
2. How would you return right-side view?
3. How would you compute the average value per level?

## Variants and extensions

- Level-order serialization.
- Breadth-first UI tree rendering.
- Batched processing of hierarchical jobs.

## Cross-links

- [BFS / DFS Overview](./01-overview.md)
- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
