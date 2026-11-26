# Sort Colors

## Clean-Room Summary

Sort an array containing only the color codes `0`, `1`, and `2` directly inside the input array.

## Driver Signature

```java
class Solution {
    public void sortColors(int[] nums) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def sortColors(self, nums: List[int]) -> None:
        # implementation
```

## Repo-Authored Examples

| nums | Mutated nums |
|---|---|
| `[1, 0, 2, 1, 0]` | `[0, 0, 1, 1, 2]` |
| `[2, 1, 0, 2, 1, 0, 0]` | `[0, 0, 0, 1, 1, 2, 2]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Selection sort | `O(n^2)`. | `O(1)`. |
| 2 | Count and overwrite | `O(n)`. | `O(1)`. |
| 3 | Dutch national flag partition | `O(n)`. | `O(1)`. |

## Pitfalls

- Counting works because there are only three possible values.
- In the three-pointer method, do not advance `mid` after swapping with `high`; the incoming value still needs classification.
- The driver checks the full mutated array because the method returns no length.
