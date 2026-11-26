# Heap / Priority Queue Overview

## Overview

Heap problems are priority-boundary problems. Instead of sorting the full collection every time, keep a structure that can expose the current minimum or maximum in `O(log n)` update time.

The first interview move is to say what the heap contains. A heap entry is often more than a value: it may include frequency, source list id, index, distance, cooldown time, or a deterministic tie-breaker.

## Requirements and constraints

- Decide whether the problem needs min priority, max priority, or both.
- Keep heap size bounded when only top `k` items are needed.
- Track stale or unavailable entries explicitly when priorities change.
- Be honest that a heap does not give fully sorted iteration unless you pop all elements or sort the result.
- In languages with only min-heaps, model max-heaps by negating numeric priorities.

## Recognition cue

"Repeatedly choose the smallest, largest, most frequent, closest, earliest available, or kth boundary item" strongly signals a heap.

## Invariant or state definition

The heap root is always the next valid candidate under the chosen priority, and all extra state explains why candidates are valid, unavailable, stale, or already emitted.

## High-level design / approach

| Question | Heap design choice |
|---|---|
| Do I need only `k` winners? | Keep a size-k heap and evict worse candidates |
| Do I need stream medians? | Maintain two ordered halves with balanced sizes |
| Do I need sorted merge? | Store one active head per sorted source |
| Do I need frequency choices? | Store remaining counts and reinsert after decrement |
| Do I need cooldown? | Pair the heap with a queue keyed by next allowed time |

## Dry run

Find the 3 largest values in `5, 1, 9, 3, 8`.

| Value | Min-heap of top 3 | Decision |
|---:|---|---|
| 5 | `[5]` | add |
| 1 | `[1, 5]` | add |
| 9 | `[1, 5, 9]` | add |
| 3 | `[3, 5, 9]` | add then evict `1` |
| 8 | `[5, 8, 9]` | add then evict `3` |

The root `5` is the 3rd largest value, and the heap contains the top 3 values.

## Language-neutral pseudocode

```text
top_k_largest(values, k):
    heap = empty min_heap
    for value in values:
        heap.push(value)
        if heap.size > k:
            heap.pop_min()
    return heap contents
```

## Complexity proof

If the heap is bounded to size `k`, each push/pop costs `O(log k)`, so scanning `n` items costs `O(n log k)` time and `O(k)` space. If the heap can grow to all `n` items, operations cost `O(log n)` and total time is often `O(n log n)`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Entry definition | Names all fields stored in the heap |
| Priority direction | Correctly chooses min-heap, max-heap, or two heaps |
| Size bound | States the heap maximum size |
| Validity | Handles stale, unavailable, or tied entries |
| Complexity | Uses the actual heap size in `log` terms |

## Common pitfalls

1. Saying "heap sort" when only top-k selection is needed.
2. Forgetting that Python-style heaps are min-heaps.
3. Comparing custom objects without a deterministic tie-breaker.
4. Returning heap array order as ranked order.
5. Keeping all items when a size-k heap is enough.

## Follow-up questions

1. What changes if the stream supports deletions?
2. How would you make output deterministic under ties?
3. When is quickselect better than a heap?
4. How would you shard a top-k computation across machines?

## Variants and extensions

- Top-k logs by score.
- Priority queue based schedulers.
- Feed ranking frontiers.
- Streaming quantile approximations.
- Lazy deletion for sliding windows.

## Cross-links

- [Heap / Priority Queue Pattern Pack](./README.md)
- [Kth Largest Element](./03-kth-largest-element.md)
- [Find Median from Data Stream](./05-find-median-from-data-stream.md)
- [Job Scheduler HLD](../../04-hld-projects/job-scheduler/)
