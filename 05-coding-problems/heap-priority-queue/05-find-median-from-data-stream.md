# Find Median from Data Stream

## Overview

Design a data structure that supports adding numbers and returning the median at any time.

Use two heaps: a max-heap for the lower half and a min-heap for the upper half. The median is either the top of the larger heap or the average of both roots.

## Requirements and constraints

- `addNum` should be better than sorting all values after every insert.
- `findMedian` should be `O(1)` after rebalancing.
- Clarify integer versus floating median for even counts.
- Handle duplicates and negative values.
- In languages with only min-heaps, store negated values for the lower-half max-heap.

## Recognition cue

"Median from a stream", "online median", or "query median after each insertion" signals two heaps.

## Invariant or state definition

All values in `lower` are less than or equal to all values in `upper`, and the heap sizes differ by at most one. Bias the extra element, when present, into `lower`; this makes odd-count median lookup consistent. `lower` is a max-heap; `upper` is a min-heap.

## High-level design / approach

1. Insert the new value into `lower` if it belongs in the lower half; otherwise insert into `upper`.
2. Rebalance so `lower` has either the same size as `upper` or exactly one extra element.
3. For odd count, return `lower.peek_max()`.
4. For even count, return the average of both roots.

## Dry run

Stream: `5, 2, 8, 1`.

| Insert | Lower max-heap | Upper min-heap | Median |
|---:|---|---|---:|
| 5 | `[5]` | `[]` | 5 |
| 2 | `[2]` | `[5]` | 3.5 |
| 8 | `[5, 2]` | `[8]` | 5 |
| 1 | `[2, 1]` | `[5, 8]` | 3.5 |

After each rebalance, every lower value is at most every upper value.

## Language-neutral pseudocode

```text
lower = empty max_heap
upper = empty min_heap

add_num(x):
    if lower is empty or x <= lower.peek_max():
        lower.push(x)
    else:
        upper.push(x)

    if lower.size > upper.size + 1:
        upper.push(lower.pop_max())
    if upper.size > lower.size:
        lower.push(upper.pop_min())

find_median():
    if lower is empty and upper is empty:
        raise no_median_available
    if lower.size > upper.size:
        return lower.peek_max()
    return average_as_float(lower.peek_max(), upper.peek_min())
```

Use widened arithmetic for `average_as_float`: in Java, cast before adding or compute `a / 2.0 + b / 2.0` so two large integers do not overflow before division.

## Complexity proof

Each insertion performs a constant number of heap operations, so `addNum` is `O(log n)`. Median lookup reads heap roots and is `O(1)`. Space is `O(n)` for all stream values.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Two heaps | Uses lower max-heap and upper min-heap |
| Ordering | Maintains lower root <= upper root |
| Balance | Keeps sizes within one |
| Median | Handles odd and even counts |
| Complexity | `O(log n)` insert, `O(1)` median |

## Common pitfalls

1. Sorting on every median query.
2. Rebalancing sizes but not preserving ordering.
3. Returning integer division for even medians when float is expected.
4. Forgetting negative values when using negation for max-heap.
5. Letting one heap get two or more elements larger than the other.

## Follow-up questions

1. How would deletions change the design?
2. How would you support sliding-window median?
3. What if memory cannot store the full stream?
4. How would approximate quantiles work at large scale?

## Variants and extensions

- Sliding window median with lazy deletion.
- Running percentile dashboards.
- Latency median tracking.
- Distributed quantile sketches.

## Cross-links

- [Heap / Priority Queue Overview](./01-overview.md)
- [Kth Largest Element](./03-kth-largest-element.md)
- [Monitoring and Observability](../../03-hld-concepts/monitoring-observability/THEORY.md)
