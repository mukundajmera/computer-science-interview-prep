# Minimum Height Trees

## Clean-Room Summary

Return all labels that can be chosen as roots of an undirected tree to produce minimum possible height.

## Driver Signature

```java
class Solution {
    public List<Integer> findMinHeightTrees(int n, int[][] edges) {
        // implement
    }
}
```

```python
class Solution:
    def findMinHeightTrees(self, n: int, edges: List[List[int]]) -> List[int]:
        # implement
```

## Repo-Authored Cases

- `single center`
- `two centers`
- `single node`
- `line of five`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Height from every root | `O(n(n+e))`. Each possible root runs a graph traversal. | `O(n+e)`. The adjacency list and BFS queue are stored. |
| 2 | Trim leaves | `O(n+e)`. Each node and edge is processed as leaves are trimmed. | `O(n+e)`. The adjacency sets and leaf queue are stored. |

## Pitfalls

- The answer can contain two centers.
- Handle n = 1 before building leaf queues.
