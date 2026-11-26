# Top K Frequent Elements

## Overview

Given a list of values and an integer `k`, return the `k` most frequent values.

The usual heap approach counts frequencies first, then keeps a min-heap of size `k` ordered by frequency. The heap root is the weakest value currently in the top-k set.

## Requirements and constraints

- Return exactly `k` values when at least `k` distinct values exist.
- Clarify tie behavior if output order matters.
- Counting frequencies costs `O(n)` time and `O(m)` space, where `m` is the number of distinct values.
- Heap size should be bounded to `k`, not all distinct values, unless you intentionally sort all counts.

## Recognition cue

"Most frequent", "top k by count", and "large input with small k" signal frequency counting plus a bounded heap.

## Invariant or state definition

After processing any set of distinct values, the heap contains the `k` highest-frequency values among those processed, and the root has the lowest frequency inside that candidate set.

## High-level design / approach

1. Build a frequency map.
2. For each `(value, count)` pair:
   - push `(count, value)` into a min-heap;
   - if heap size exceeds `k`, pop the smallest count.
3. Extract values from the heap.
4. Sort extracted values by frequency only if the prompt requires ranked output.

## Dry run

Input: `[1, 1, 1, 2, 2, 3, 4, 4]`, `k = 2`.

Frequencies: `1 -> 3`, `2 -> 2`, `3 -> 1`, `4 -> 2`.

| Pair | Heap by count | Decision |
|---|---|---|
| `(1, 3)` | `[(3, 1)]` | keep |
| `(2, 2)` | `[(2, 2), (3, 1)]` | keep |
| `(3, 1)` | `[(2, 2), (3, 1)]` | push then evict count `1` |
| `(4, 2)` | two of count `2` and count `3` | tie depends on rule |

Valid top values include `1` and either `2` or `4` if ties are unspecified.

## Language-neutral pseudocode

```text
counts = frequency_map(values)
heap = empty min_heap ordered by count
for value, count in counts:
    heap.push((count, value))
    if heap.size > k:
        heap.pop_min()
answer = []
while heap not empty:
    answer.append(heap.pop_min().value)
return answer
```

## Complexity proof

Counting `n` values costs `O(n)`. Processing `m` distinct values with a heap of size at most `k` costs `O(m log k)`. Extra space is `O(m + k)` for the frequency map and heap. If `k` is close to `m`, sorting all frequencies in `O(m log m)` may be simpler.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Counting | Builds a frequency map before heap work |
| Heap bound | Keeps heap size at `k` |
| Ties | States whether any tied result is acceptable |
| Output | Does not claim heap array is sorted |
| Complexity | Uses `m` distinct values and `log k` |

## Common pitfalls

1. Sorting the original array instead of counting.
2. Using a max-heap of all values when a size-k min-heap is requested for scale.
3. Forgetting `k = 0`.
4. Returning more than `k` elements because of ties.
5. Losing determinism when tests expect a tie-breaker.

## Follow-up questions

1. How would you solve this with bucket sort?
2. What if input arrives as a stream?
3. How would you merge top-k frequencies from many shards?
4. How would approximate heavy hitters change the design?

## Variants and extensions

- Top k words by frequency.
- Most frequent error codes in logs.
- Heavy hitters in telemetry streams.
- Feed topics ranked by engagement.

## Cross-links

- [Heap / Priority Queue Overview](./01-overview.md)
- [K Closest Points](./08-k-closest-points.md)
- [Realtime Metrics Platform HLD](../../04-hld-projects/realtime-metrics-platform/)
