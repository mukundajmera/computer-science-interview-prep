# Meeting Rooms II

## Clean-Room Summary

Return the minimum number of rooms needed to host all intervals without time overlap in the same room.

## Driver Signature

```java
class Solution {
    public int minMeetingRooms(int[][] intervals) {
        // implement
    }
}
```

```python
class Solution:
    def minMeetingRooms(self, intervals: List[List[int]]) -> int:
        # implement
```

## Repo-Authored Cases

- `overlapping burst`
- `adjacent meetings reuse room`
- `three simultaneous rooms`
- `unsorted intervals`
- `empty schedule`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sweep line | `O(n log n)`. Sorting the events dominates. | `O(n)`. Two events are stored for every interval. |
| 2 | Min-heap end times | `O(n log n)`. Sorting plus heap operations over intervals dominate. | `O(n)`. The heap can hold all active room end times. |

## Pitfalls

- End events at the same time as start events must free a room first.
- Input order is not meaningful.
