# Majority Element

## Clean-Room Summary

Return the value that appears more than half of the time in an integer array. The caller provides inputs where such a value exists.

## Driver Signature

```java
class Solution {
    public int majorityElement(int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Expected | Notes |
|---|---:|---|
| `[6, 1, 6, 6, 2]` | `6` | The value `6` appears in more than half the positions. |
| `[4, 4, 7, 4, 8, 4, 4]` | `4` | The majority can be interrupted by other values. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Count occurrences in a map | `O(n)` because each element is counted once. | `O(k)` for `k` distinct values. |
| 2 | Boyer-Moore voting | `O(n)` because the array is scanned once. | `O(1)` because only a candidate and counter are stored. |
