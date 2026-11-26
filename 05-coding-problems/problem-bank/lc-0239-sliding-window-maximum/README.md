# Sliding Window Maximum

## Clean-Room Summary

Return the maximum value in every contiguous window of size k.

## Driver Signature

```java
class Solution {
    public int[] maxSlidingWindow(int[] nums, int k) {
        // implement
    }
}
```

```python
class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        # implement
```

## Repo-Authored Cases

- `mixed signs and rises`
- `single element window`
- `strictly decreasing`
- `whole array window`
- `duplicates in queue`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Scan each window | `O(nk)`. There are n-k+1 windows and each scan can inspect k values. | `O(1)`. Only the output and loop counters are stored. |
| 2 | Monotonic deque | `O(n)`. Each index is inserted and removed at most once. | `O(k)`. The deque stores at most k window indices. |

## Pitfalls

- Store indices so expired values can be removed.
- Pop smaller or equal values from the back before appending a new index.
