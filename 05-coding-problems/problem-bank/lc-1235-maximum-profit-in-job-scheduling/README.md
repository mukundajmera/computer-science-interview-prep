# Maximum Profit in Job Scheduling

## Clean-Room Summary

Choose a subset of non-overlapping half-open jobs that maximizes total profit.

## Driver Signature

```java
class Solution {
    public int jobScheduling(int[] startTime, int[] endTime, int[] profit) {
        // implement
    }
}
```

```python
class Solution:
    def jobScheduling(self, startTime: List[int], endTime: List[int], profit: List[int]) -> int:
        # implement
```

## Repo-Authored Cases

- `choose first and last`
- `chain around long job`
- `same start choose best`
- `all non overlapping`
- `touching intervals compatible`
- `single job`
- `unsorted input chain`
- `duplicate start longer is better`
- `duplicate compatible boundary`
## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Quadratic DP | `O(n^2)`. Each job can compare against every earlier job. | `O(n)`. Sorted jobs and one DP array are stored. |
| 2 | Binary-search DP | `O(n log n)`. Sorting and one binary search per job dominate. | `O(n)`. The sorted jobs, end-time array, and DP table are stored. |

## Pitfalls

- A job ending exactly when another starts is compatible.
- Sorting by start time requires a different recurrence; these solutions sort by end time.
