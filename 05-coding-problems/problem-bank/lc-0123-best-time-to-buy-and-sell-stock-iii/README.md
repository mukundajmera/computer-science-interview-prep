# Best Time to Buy and Sell Stock III

## Clean-Room Summary

Given daily prices, return the largest profit obtainable with at most two non-overlapping buy/sell transactions.

## Driver Signature

```java
class Solution {
    public int maxProfit(int[] prices) {
        // implementation
    }
}
```

```python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `[1, 5, 2, 8, 4, 9]` | `12` |
| `[7, 6, 4, 3, 1]` | `0` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Prefix and suffix one-transaction profits | `O(n)`. Two linear scans precompute best profit before and after each split. | `O(n)`. Two helper arrays store prefix and suffix profits. |
| 2 | Four-state scan | `O(n)`. Each price updates first buy, first sell, second buy, and second sell states once. | `O(1)`. Only four profit states are stored. |

## Pitfalls

- Transactions cannot overlap: the second buy must happen after the first sell.
- Returning zero is valid when every transaction would lose money.
- The four-state variables model cash after actions, not actual held shares.
