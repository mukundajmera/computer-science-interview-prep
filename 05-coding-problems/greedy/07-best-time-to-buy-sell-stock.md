# Best Time to Buy and Sell Stock

## Overview

Given daily prices, return the maximum profit from one buy followed by one sell.

The greedy invariant is the minimum price seen before the current day. Selling today is only useful relative to the best previous buy.

## Requirements and constraints

- Buy before sell.
- At most one transaction.
- Return `0` if no profitable transaction exists.
- Prefer `O(n)` time and `O(1)` space.

## Recognition cue

"Maximum profit with one transaction" signals min-so-far greedy.

## Proof idea

For a fixed sell day, the best buy day is the lowest price before it. No higher previous price can improve profit for the same sell day. Scanning left to right preserves exactly the future-relevant fact: minimum buy price so far.

## Wrong greedy counterexample

Sorting prices fails because it destroys time order. Prices `[5, 1, 4]` support profit `3`, but a sorted view would pretend any low price can pair with any high price and can accidentally allow selling before buying on other inputs.

## High-level design / approach

1. Set `min_price = infinity`.
2. Set `best_profit = 0`.
3. For each price:
   - compute profit if selling today: `price - min_price`;
   - update `best_profit`;
   - update `min_price`.
4. Return `best_profit`.

## Dry run

Prices: `[7, 1, 5, 3, 6, 4]`.

| Day price | Min before/after | Best profit |
|---:|---:|---:|
| 7 | 7 | 0 |
| 1 | 1 | 0 |
| 5 | 1 | 4 |
| 3 | 1 | 4 |
| 6 | 1 | 5 |
| 4 | 1 | 5 |

Answer: `5`.

## Language-neutral pseudocode

```text
min_price = infinity
best = 0
for price in prices:
    best = max(best, price - min_price)
    min_price = min(min_price, price)
return best
```

If your language cannot subtract from infinity safely, update `min_price` before or initialize with the first price and scan from the second.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Ordering | Enforces buy before sell |
| Dominance | Keeps lowest prior buy price |
| Edge cases | Handles decreasing prices and short input |
| Complexity | One pass and constant space |

## Common pitfalls

1. Sorting prices and losing time order.
2. Allowing sell before buy.
3. Returning negative profit.
4. Confusing one transaction with unlimited transactions.

## Follow-up questions

1. What changes for unlimited transactions?
2. What changes with transaction fees?
3. What changes with cooldown days?

## Variants and extensions

- Pricing-window optimization.
- Buy-low/sell-high signal scans.
- Threshold alerts over time-series streams.

## Cross-links

- [Greedy Overview](./01-overview.md)
- [Price Tracking Service HLD](../../04-hld-projects/price-tracking-service/)
