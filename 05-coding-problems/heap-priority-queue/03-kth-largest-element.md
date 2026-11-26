# Kth Largest Element

## Overview

Given an unsorted array and integer `k`, return the kth largest value.

A min-heap of size `k` is the standard heap solution. Values larger than the root belong in the top-k frontier; values smaller than or equal to the root cannot affect the kth largest once the heap is full.

## Requirements and constraints

- Clarify whether `k` is 1-indexed. In most prompts, `k = 1` means maximum.
- Duplicates count as separate elements unless the prompt says kth distinct.
- Reject or guard invalid `k` values outside `1..n`.
- Prefer `O(n log k)` heap time when `k` is small; quickselect can be `O(n)` average but is not a heap pattern.

## Recognition cue

"Kth largest in an unsorted array" strongly signals a size-k min-heap or quickselect. Choose heap when streaming or predictable worst-case behavior is useful.

## Invariant or state definition

After scanning each value, the heap contains the `k` largest values seen so far. When the heap has size `k`, its root is the kth largest among scanned values.

## High-level design / approach

1. Initialize an empty min-heap.
2. For each value:
   - push it into the heap;
   - if heap size exceeds `k`, pop the smallest value.
3. Return heap root after all values are processed.

## Dry run

Input: `[3, 2, 1, 5, 6, 4]`, `k = 2`.

| Value | Heap | Meaning |
|---:|---|---|
| 3 | `[3]` | top 1 so far |
| 2 | `[2, 3]` | top 2 so far |
| 1 | `[2, 3]` | `1` evicted |
| 5 | `[3, 5]` | `2` evicted |
| 6 | `[5, 6]` | `3` evicted |
| 4 | `[5, 6]` | `4` evicted |

The 2nd largest is `5`.

## Language-neutral pseudocode

```text
if k < 1 or k > length(values): error
heap = empty min_heap
for value in values:
    heap.push(value)
    if heap.size > k:
        heap.pop_min()
return heap.peek_min()
```

## Complexity proof

Each of `n` values causes at most one push and one pop on a heap of size `k + 1`, so time is `O(n log k)`. Extra space is `O(k)`.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Indexing | Clarifies kth largest and duplicate handling |
| Heap choice | Uses min-heap, not max-heap of all values |
| Invariant | Root is kth largest only after size reaches `k` |
| Invalid input | Handles `k` outside range |
| Complexity | Gives `O(n log k)` and `O(k)` |

## Common pitfalls

1. Building a max-heap and popping `k` times when size-k heap was expected.
2. Treating duplicates as distinct incorrectly.
3. Returning before all values are scanned.
4. Off-by-one errors for `k = 1`.
5. Forgetting that heap root is smallest among the kept top-k values.

## Follow-up questions

1. How would quickselect compare?
2. What if values arrive as a stream?
3. What if you need kth largest distinct value?
4. How would you support deletions from the stream?

## Variants and extensions

- Kth largest in a stream.
- Kth smallest by using a max-heap of size `k`.
- Top-k ranked documents.
- Leaderboard threshold computation.

## Cross-links

- [Heap / Priority Queue Overview](./01-overview.md)
- [Top K Frequent Elements](./02-top-k-frequent-elements.md)
- [Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
