# Coin Change

## Overview

Given coin denominations and an amount, return the fewest coins needed to make that amount. Return `-1` if impossible.

This is minimum-count DP over amounts. Each state asks: "What is the minimum number of coins needed for this amount?"

## Requirements and constraints

- Coins can be used unlimited times.
- Return minimum coin count, not the list of coins.
- Return `-1` when amount cannot be formed.
- Prefer `O(amount * number_of_coins)` time.

## Recognition cue

"Fewest items to make a target" with reusable choices signals DP, not greedy, unless the coin system has a proven greedy property.

## State definition

`dp[a]` is the minimum number of coins needed to make amount `a`. Impossible states use infinity.

## High-level design / approach

1. Set `dp[0] = 0`.
2. Set all other amounts to infinity.
3. For each amount from `1` to target:
   - try every coin `c`;
   - if `a - c >= 0`, candidate is `dp[a - c] + 1`.
4. Return `dp[amount]` if finite, else `-1`.

## Dry run

Coins: `[1, 3, 4]`, amount `6`.

| Amount | Best calculation | `dp` |
|---:|---|---:|
| 0 | base | 0 |
| 1 | `dp[0] + 1` | 1 |
| 2 | `dp[1] + 1` | 2 |
| 3 | coin 3 from `0` | 1 |
| 4 | coin 4 from `0` | 1 |
| 5 | coin 4 from `1` or coin 3 from `2` | 2 |
| 6 | coin 3 from `3` | 2 |

Answer: `2`.

## Language-neutral pseudocode

```text
dp = array amount + 1 filled with infinity
dp[0] = 0
for a from 1 to amount:
    for coin in coins:
        if a - coin >= 0:
            dp[a] = min(dp[a], dp[a - coin] + 1)
return -1 if dp[amount] is infinity else dp[amount]
```

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| State | Defines min coins for each amount |
| Impossible sentinel | Uses infinity instead of ambiguous zero |
| Transition | Tries every coin as the last coin |
| Complexity | `O(amount * coins)` time, `O(amount)` space |

## Common pitfalls

1. Using greedy with denominations like `[1, 3, 4]`.
2. Forgetting `dp[0] = 0`.
3. Returning infinity for impossible targets.
4. Mixing this minimum-count problem with count-the-number-of-combinations.

## Follow-up questions

1. How would you count combinations instead of minimum coins?
2. How would you return the chosen coins?
3. What if each coin can be used only once?

## Variants and extensions

- Combination Sum IV.
- Knapsack-style budget optimization.
- Cost/latency trade-off selection under a budget.

## Cross-links

- [Dynamic Programming Overview](./01-overview.md)
- [Token / Cost / Latency Planning](../../06-genai-systems/00-concepts/token-cost-latency/README.md)
