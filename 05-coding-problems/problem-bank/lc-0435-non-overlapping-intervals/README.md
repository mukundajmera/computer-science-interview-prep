# Non-overlapping Intervals

## Clean-Room Summary

Return the fewest intervals to remove so the remaining intervals have no positive overlap.

## Driver Signature

```java
class Solution {
    public int eraseOverlapIntervals(int[][] intervals) {
        // implement
    }
}
```

```python
class Solution:
    def eraseOverlapIntervals(self, intervals: List[List[int]]) -> int:
        # implement
```

## Repo-Authored Cases

- `remove one middle overlap`
- `all same interval`
- `touching endpoints allowed`
- `negative intervals`
- `choose shorter interval for future`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Longest compatible DP | `O(n^2)`. Every interval can be compared with every earlier interval. | `O(n)`. The DP table stores one value per interval. |
| 2 | Greedy earliest end | `O(n log n)`. Sorting dominates the linear selection pass. | `O(log n)`. Sorting may use recursion or temporary stack space. |

## Pitfalls

- Intervals that touch at an endpoint are compatible.
- Keeping the interval with the earliest end leaves maximum room for future intervals.
