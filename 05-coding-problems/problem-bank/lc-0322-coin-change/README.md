# Coin Change

## Clean-Room Summary

Given coin denominations and a target amount, return the minimum number of coins needed to make that amount, or -1 if it cannot be made.

## Driver Signature

```java
class Solution {
    public int coinChange(int[] coins, int amount) {
        // implementation
    }
}
```

```python
class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `coins = [2, 4, 7]`, `amount = 13` | `3` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | BFS over reachable amounts | `O(amount * c)`. Each reachable amount can expand up to c coin denominations. | `O(amount)`. Visited amounts and the queue are bounded by amount + 1 states. |
| 2 | Bottom-up minimum coins DP | `O(amount * c)`. For each amount, every denomination can be tested. | `O(amount)`. The DP table stores one minimum count for each amount. |

## Pitfalls

- Use amount + 1 or another sentinel larger than any valid answer.
- Order of coins does not matter for the count; this is not a permutation problem.
- Amount zero needs zero coins even when no denomination is used.
