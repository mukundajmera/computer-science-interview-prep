# Search in Rotated Sorted Array

## Clean-Room Summary

Given a sorted array that has been rotated at an unknown pivot and a target value, return the target index or -1 if it is absent.

## Driver Signature

```java
class Solution {
    public int search(int[] nums, int target) {
        // implementation
    }
}
```

```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `nums = [10, 14, 2, 4, 6, 8]`, `target = 4` | `3` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Linear scan | `O(n)`. The scan may inspect all n values when the target is absent or near the end. | `O(1)`. Only a loop index is stored. |
| 2 | Rotated binary search | `O(log n)`. Each comparison removes about half of the remaining search range. | `O(1)`. The search uses only two boundaries and a midpoint. |

## Pitfalls

- At least one half around the midpoint is sorted; use that fact to discard half the range.
- Compare target against the sorted half boundaries before moving pointers.
- Return the actual array index, not the position inside an unrotated view.
