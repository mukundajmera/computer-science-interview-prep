# Best Time to Buy and Sell Stock II

## Clean-Room Summary

Given daily stock prices and permission to complete multiple non-overlapping buy/sell trades, return the maximum total profit.

## Driver Signature

```java
class Solution {
    public int maxProfit(int[] prices) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| prices | Max profit |
|---|---:|
| `[3, 1, 4, 8, 2, 5]` | `10` |
| `[9, 7, 4]` | `0` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Hold/cash dynamic state | `O(n)`. | `O(1)`. |
| 2 | Sum every positive daily gain | `O(n)`. | `O(1)`. |

## Pitfalls

- Selling before buying is not allowed, so each gain must come from an upward adjacent move or equivalent state transition.
- A decreasing sequence has zero profit.
- Multiple profitable rises can all be captured because trades do not overlap when each sale happens before the next buy.
