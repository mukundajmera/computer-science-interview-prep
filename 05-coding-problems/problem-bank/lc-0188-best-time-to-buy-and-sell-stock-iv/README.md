# Best Time to Buy and Sell Stock IV

## Clean-Room Summary

Given a transaction limit and daily prices, return the largest profit obtainable with no more than that many non-overlapping buy/sell transactions.

## Driver Signature

```java
class Solution {
    public int maxProfit(int k, int[] prices) {
        // implementation
    }
}
```

```python
class Solution:
    def maxProfit(self, k: int, prices: List[int]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `k=2, prices=[1, 5, 2, 8, 4, 9]` | `12` |
| `k=1, prices=[1, 5, 2, 8]` | `7` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Quadratic transaction DP | `O(k*n^2)`. For each transaction count and sell day, every earlier buy day may be tested. | `O(k*n)`. The DP table stores profit for every transaction/day state. |
| 2 | Optimized transaction DP | `O(k*n)`. Each transaction layer maintains the best prior balance while scanning days. | `O(k*n)`. The table can be retained for clarity and reconstruction-friendly state. |

## Pitfalls

- When `k` is at least half the number of days, the problem reduces to unlimited ascending gains.
- The transaction count increases only after a completed sell.
- Buying and selling on the same day never improves profit but can simplify state transitions.
