# Clone Graph

## Clean-Room Summary

Deep-copy a connected undirected graph. The returned graph must preserve every node value and neighbor relationship without reusing original node objects.

## Driver Signature

```java
class Solution {
    public Node cloneGraph(Node node) {
        // return copied graph entry node
    }
}
```

```python
from typing import Optional


class Solution:
    def cloneGraph(self, node: Optional[Node]) -> Optional[Node]:
        # return copied graph entry node
```

## Repo-Authored Examples

Fixtures use 1-based adjacency lists. Row `i` lists the neighbors of node `i + 1`.

| Input adjacency | Expected copy |
|---|---|
| `[[2,3],[1,3],[1,2]]` | `[[2,3],[1,3],[1,2]]` |
| `[[2],[1,3,4],[2,4],[2,3]]` | `[[2],[1,3,4],[2,4],[2,3]]` |
| `[]` | `[]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | DFS clone with map | `O(V + E)`. Clone each node and scan each edge once. | `O(V)`. Map plus recursion stack. |
| 2 | BFS clone with queue | `O(V + E)`. Iteratively process each node and neighbor reference. | `O(V)`. Map and queue. |

## Pitfalls

- A graph cycle must not cause infinite recursion.
- Returning an original node is invalid even if adjacency values look correct.
- Create each clone before wiring neighbors so cycles can point to existing clone placeholders.
