# Two Sum II - Input Array Is Sorted

## Clean-Room Summary

Given a sorted integer array and target, return the one-based indices of the two numbers that add to the target.

## Driver Signature

```java
class Solution {
    public int[] twoSum(int[] numbers, int target) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| numbers | target | Indices |
|---|---:|---|
| `[1, 4, 6, 9, 13]` | `15` | `[3, 4]` |
| `[2, 5, 8, 11]` | `13` | `[1, 4]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Binary search each complement | `O(n log n)`. | `O(1)`. |
| 2 | Two pointers from both ends | `O(n)`. | `O(1)`. |

## Pitfalls

- Returned indices are one-based, not zero-based.
- The sorted order enables pointer movement based on whether the current sum is too small or too large.
- The pair is assumed to exist under the problem contract.
