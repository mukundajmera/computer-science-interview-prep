# Course Schedule II

## Clean-Room Summary

Return one valid order to take all courses, or an empty order when prerequisite cycles make completion impossible.

## Driver Signature

```java
class Solution {
    public int[] findOrder(int numCourses, int[][] prerequisites) {
        // implementation
    }
}
```

```python
class Solution:
    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `numCourses = 4, prerequisites = [[1,0],[2,1],[3,2]]` | `[0,1,2,3]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | DFS postorder | `O(V+E)`. Each course and prerequisite edge is traversed at most once. | `O(V+E)`. The adjacency list, state array, recursion stack, and output order are stored. |
| 2 | Kahn queue | `O(V+E)`. Each course is queued once and each prerequisite edge is processed once. | `O(V+E)`. The adjacency list, indegrees, queue, and result are stored. |

## Pitfalls

- Multiple valid orders may exist, so deterministic cases should avoid ambiguous independent choices.
- Return an empty array/list when a cycle prevents using every course.
- DFS postorder must be reversed when edges go from prerequisite to dependent course.
