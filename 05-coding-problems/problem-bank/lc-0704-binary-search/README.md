# Binary Search

## Clean-Room Summary

Given an ascending sorted integer array and a target, return the target index if present; otherwise return -1.

## Driver Signature

```java
class Solution {
    public int search(int[] nums, int target) {
        // implement
    }
}
```

```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        # implement
```

## Repo-Authored Cases

- `target in the middle`
- `target below range`
- `single element hit`
- `single element miss`
- `negative values`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Binary search | `O(log n)`. Each comparison halves the remaining search interval. | `O(1)`. The search stores only two boundaries. |

## Pitfalls

- Use `left + (right - left) / 2` in Java to avoid overflow style issues.
- Keep the loop condition closed: `left <= right`.
- Return `-1` only after the interval is empty.
