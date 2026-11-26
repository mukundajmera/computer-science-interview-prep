# Meeting Rooms

## Clean-Room Summary

Given meeting time intervals, return whether one person can attend every meeting without any overlap.

## Driver Signature

```java
class Solution {
    public boolean canAttendMeetings(int[][] intervals) {
        // implement
    }
}
```

```python
class Solution:
    def canAttendMeetings(self, intervals: List[List[int]]) -> bool:
        # implement
```

## Repo-Authored Cases

- `no meetings`
- `non overlapping adjacent meetings`
- `direct overlap`
- `unsorted overlap`
- `single meeting`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Compare all pairs | `O(n^2)`. Every pair of meetings can be compared. | `O(1)`. Only loop counters are stored beyond the input. |
| 2 | Sort by start | `O(n log n)`. Sorting dominates the linear overlap scan. | `O(log n)`. The Java sort may use stack space; Python uses a sorted copy in the driver-isolated input. |

## Pitfalls

- Adjacent intervals where one end equals the next start do not overlap.
- Sort before scanning; input order is not guaranteed.
