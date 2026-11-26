# Search Insert Position

## Clean-Room Summary

Given a sorted array with distinct values, return the index of a target or where it should be inserted to keep order.

## Driver Signature

```java
class Solution {
    public int searchInsert(int[] nums, int target) {
        // implementation
    }
}
```

```python
class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `nums = [2, 5, 9, 14]`, `target = 7` | `2` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Linear lower-bound scan | `O(n)`. The scan may inspect every element before deciding the insertion position. | `O(1)`. Only a loop index is used. |
| 2 | Binary search lower bound | `O(log n)`. Each iteration halves the remaining search range. | `O(1)`. The search uses constant extra variables. |

## Pitfalls

- Return the left boundary after binary search; it is the first index whose value is not smaller than target.
- Handle insertion before the first element and after the last element.
- Do not assume the target is always present.
