# 3Sum

## Clean-Room Summary

Return all unique triplets of values whose sum is zero.

## Driver Signature

```java
class Solution {
    public List<List<Integer>> threeSum(int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        # implementation
```

## Repo-Authored Examples

| nums | triplets |
| --- | --- |
| `[-2, -1, 0, 1, 2, 3]` | `[[-2, -1, 3], [-2, 0, 2], [-1, 0, 1]]` |
| `[0, 0, 0, 0]` | `[[0, 0, 0]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Cubic enumeration with set deduplication | `O(n^3)`. | `O(k)`. |
| 2 | Sort plus two pointers | `O(n^2)`. | `O(k)`. |

## Pitfalls

- Triplets must be unique by value, not by source indices.
- Sorting enables duplicate skipping and ordered output.
- After finding a match, move both inner pointers past duplicate values.
