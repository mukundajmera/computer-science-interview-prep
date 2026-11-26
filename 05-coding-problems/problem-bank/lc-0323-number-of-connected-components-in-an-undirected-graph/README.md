# Number of Connected Components in an Undirected Graph

## Clean-Room Summary

Count how many connected components exist in an undirected graph with nodes labeled from 0 to n - 1.

## Driver Signature

```java
class Solution {
    public int countComponents(int n, int[][] edges) {
        // implement
    }
}
```

```python
class Solution:
    def countComponents(self, n: int, edges: List[List[int]]) -> int:
        # implement
```

## Repo-Authored Cases

- `two components`
- `all isolated`
- `one connected component`
- `cycle still one component`
- `mixed isolated and connected`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | DFS components | `O(n+e)`. Every node and edge is visited at most once. | `O(n+e)`. The adjacency list and visited set are stored. |
| 2 | Union-Find | `O(n+e alpha(n))`. Union-Find operations are nearly constant time. | `O(n)`. Parent and rank arrays store one entry per node. |

## Pitfalls

- Cycles do not create extra components.
- Isolated nodes count as single-node components.
