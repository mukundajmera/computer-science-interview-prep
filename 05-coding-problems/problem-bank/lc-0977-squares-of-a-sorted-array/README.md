# Squares of a Sorted Array

## Clean-Room Summary

Square every value from a sorted integer array and return the squares in nondecreasing order.

## Driver Signature

```java
class Solution {
    public int[] sortedSquares(int[] nums) {
        // implement
    }
}
```

```python
class Solution:
    def sortedSquares(self, nums: List[int]) -> List[int]:
        # implement
```

## Repo-Authored Cases

- `mixed signs`
- `all negative`
- `all non negative`
- `duplicate absolute values`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Square and sort | `O(n log n)`. Sorting the squared values dominates. | `O(n)`. The output array stores n squared values. |
| 2 | Two pointers | `O(n)`. Each value is placed exactly once. | `O(n)`. The result array stores n values. |

## Pitfalls

- The largest square may come from either end because negative values can have large magnitude.
- Fill from the back to avoid reversing at the end.
