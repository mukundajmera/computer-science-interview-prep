# Course Schedule

## Clean-Room Summary

Given course count and prerequisite pairs, return whether every course can be completed without a prerequisite cycle.

## Driver Signature

```java
class Solution {
    public boolean canFinish(int numCourses, int[][] prerequisites) {
        // implementation
    }
}
```

```python
class Solution:
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `numCourses = 5, prerequisites = [[1,0],[2,0],[3,1],[3,2],[4,3]]` | `true` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | DFS cycle states | `O(V+E)`. Each course and prerequisite edge is visited at most once. | `O(V+E)`. The graph plus DFS recursion/state arrays are stored. |
| 2 | Kahn topological count | `O(V+E)`. Each course enters the queue once and each edge lowers one indegree. | `O(V+E)`. The adjacency list, indegrees, and queue are stored. |

## Pitfalls

- Edges point from prerequisite to dependent course for topological ordering.
- A node currently on the DFS recursion path means a cycle, not merely a previously visited node.
- Disconnected components still need to be checked.
