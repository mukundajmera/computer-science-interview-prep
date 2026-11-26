# Candy

## Clean-Room Summary

Given child ratings in order, assign at least one candy to each child so every higher-rated child has more candy than each immediate lower-rated neighbor, and minimize the total candies.

## Driver Signature

```java
class Solution {
    public int candy(int[] ratings) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def candy(self, ratings: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| ratings | minimum candies |
| --- | ---: |
| `[2, 4, 3, 5]` | `6` |
| `[5, 4, 3, 2]` | `10` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Two directional candy arrays | `O(n)`. | `O(n)`. |
| 2 | One candy array with reverse correction | `O(n)`. | `O(n)`. |

## Pitfalls

- Both left and right neighbor rules must hold at the same time.
- A local peak may need candies from the larger of the two directional passes.
- Equal ratings do not force a strict candy difference.
