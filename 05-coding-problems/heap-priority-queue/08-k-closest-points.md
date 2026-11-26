# K Closest Points

## Overview

Given points on a plane and integer `k`, return the `k` points closest to the origin.

Use a max-heap of size `k` ordered by squared distance. The root is the farthest point among the kept closest candidates, so any new point closer than the root replaces it.

## Requirements and constraints

- Squared distance `x*x + y*y` is enough; no square root is needed.
- Return any order unless the prompt requires sorted output.
- Clarify tie behavior if distances are equal; include a stable scalar tie-breaker when deterministic output is required.
- Use a max-heap of size `k` for `O(n log k)` time, or quickselect for average `O(n)` when allowed.

## Recognition cue

"K closest", "nearest points", "top k by distance", and "large point set with small k" signal bounded heap selection.

## Invariant or state definition

After scanning each point, the max-heap contains the `k` closest points seen so far, and the root is the farthest among those kept points.

## High-level design / approach

1. For each point, compute squared distance.
2. Push `(distance, stable_id, point)` into a max-heap so ties never compare raw point objects.
3. If heap size exceeds `k`, pop the farthest point.
4. Return points remaining in the heap.

## Dry run

Points: `(1,3)`, `(-2,2)`, `(5,8)`, `(0,1)`, `k = 2`.

Squared distances: `10`, `8`, `89`, `1`.

| Point | Heap of closest 2 by farthest root | Decision |
|---|---|---|
| `(1,3)` | `10` | keep |
| `(-2,2)` | `10, 8` | keep |
| `(5,8)` | `10, 8` | distance `89` evicted |
| `(0,1)` | `8, 1` | distance `10` evicted |

Answer: `(-2,2)` and `(0,1)`.

## Language-neutral pseudocode

```text
heap = empty max_heap ordered by distance
for stable_id, point in enumerate(points):
    dist = point.x * point.x + point.y * point.y
    heap.push((dist, stable_id, point))
    if heap.size > k:
        heap.pop_max()
return [entry.point for entry in heap]
```

## Complexity proof

Each of `n` points causes heap work over at most `k + 1` entries, so time is `O(n log k)`. Extra heap space is `O(k)`. Distance computation is `O(1)` per point.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Distance | Uses squared distance |
| Heap choice | Uses size-k max-heap for closest points |
| Output order | States order is arbitrary unless required |
| Ties | Uses a stable scalar tie-breaker instead of raw point comparison when deterministic output is required |
| Complexity | Gives `O(n log k)` and `O(k)` |

## Common pitfalls

1. Using square root unnecessarily.
2. Keeping a min-heap and accidentally retaining farthest points.
3. Returning sorted order without paying sorting cost.
4. Failing when `k == n` or `k == 0`.
5. Overflowing squared distance in fixed-width integer languages.
6. Relying on tuple/object comparison of raw point payloads when distances tie.

## Follow-up questions

1. How would quickselect compare?
2. How would you find nearest points to an arbitrary query point?
3. How would this work for streaming points?
4. What spatial index would you consider for many repeated queries?

## Variants and extensions

- K nearest restaurants.
- Nearest log events by timestamp distance.
- Search result reranking by score distance.
- Geo-index pruning before heap selection.

## Cross-links

- [Heap / Priority Queue Overview](./01-overview.md)
- [Top K Frequent Elements](./02-top-k-frequent-elements.md)
- [Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
