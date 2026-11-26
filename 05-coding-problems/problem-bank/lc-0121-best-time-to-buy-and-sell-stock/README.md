# Best Time to Buy and Sell Stock

## Clean-Room Summary

Given daily prices for one asset, choose one buy day before one sell day to maximize profit. Return `0` when no profitable trade exists.

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

| Input | Expected | Notes |
|---|---:|---|
| `[8, 2, 4, 1, 9, 3]` | `8` | Buy at `1`, sell at `9`. |
| `[9, 7, 4, 3]` | `0` | Prices never recover after an earlier day. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Check every buy/sell pair | `O(n^2)` because every later sell day is compared with each buy day. | `O(1)` because only counters and the best profit are stored. |
| 2 | Track lowest previous price | `O(n)` because each price is processed once. | `O(1)` because the minimum price and best profit are scalars. |
