# K Closest Points to Origin

## Clean-Room Summary

Return any k points with the smallest squared Euclidean distance from the origin.

## Driver Signature

```java
class Solution {
    public int[][] kClosest(int[][] points, int k) {
        // implement
    }
}
```

```python
class Solution:
    def kClosest(self, points: List[List[int]], k: int) -> List[List[int]]:
        # implement
```

## Repo-Authored Cases

- `two closest without ties`
- `keeps all tied boundary points included`
- `single closest point`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sort by distance | `O(n log n)`. Sorting n points dominates the work. | `O(n)`. The sorted copy or sort internals can store up to n point references. |
| 2 | Size-k max heap | `O(n log k)`. Each point performs at most one heap insertion and possibly one removal from a size-k heap. | `O(k)`. Only k candidate points are retained. |

## Pitfalls

- Compare squared distances; square roots are unnecessary.
- The returned point order is not meaningful, so tests use unordered nested-list matching.
- For heap solutions, keep only k points to get the intended space bound.
