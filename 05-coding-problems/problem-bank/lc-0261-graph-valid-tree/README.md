# Graph Valid Tree

## Clean-Room Summary

Given an undirected graph with n labeled nodes, return whether the edges form exactly one connected acyclic component.

## Driver Signature

```java
class Solution {
    public boolean validTree(int n, int[][] edges) {
        // implement
    }
}
```

```python
class Solution:
    def validTree(self, n: int, edges: List[List[int]]) -> bool:
        # implement
```

## Repo-Authored Cases

- `simple valid tree`
- `cycle invalid`
- `disconnected invalid`
- `single node`
- `too many edges`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | DFS connectivity cycle | `O(n+e)`. The adjacency list and traversal visit each node and edge. | `O(n+e)`. The graph and visited set are stored. |
| 2 | Union-Find | `O(n+e alpha(n))`. Union-Find operations are nearly constant time. | `O(n)`. Parent and rank arrays store one entry per node. |

## Pitfalls

- A tree with n nodes must have exactly n - 1 edges.
- Acyclic alone is not enough; all nodes must be connected.
