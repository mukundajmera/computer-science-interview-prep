# Merge K Sorted Lists

## Overview

Given `k` sorted linked lists or arrays, merge them into one sorted output.

The heap stores only the current head from each active list. The root is the smallest available value globally because every list is already sorted internally.

## Requirements and constraints

- Inputs may include empty lists.
- Output may reuse existing nodes or allocate new nodes; clarify mutation rules.
- Preserve duplicates.
- Heap size is at most the number of active lists, not the total number of elements.

## Recognition cue

"Merge k sorted lists", "combine sorted feeds", or "smallest next item among sorted sources" signals a k-way merge heap.

## Invariant or state definition

The heap contains the next unmerged node or value from each active sorted source. The heap root is the next value that must appear in the merged output.

## High-level design / approach

1. Push the first node or first element from each non-empty list into a min-heap.
2. Repeatedly pop the smallest heap entry.
3. Append that value or node to the output.
4. If the popped entry has a next element in its source, push that next element.
5. Stop when the heap is empty.

## Dry run

Lists: `[1,4,5]`, `[1,3,4]`, `[2,6]`.

| Pop | Push next | Output | Heap heads |
|---:|---|---|---|
| 1 from A | 4 from A | `[1]` | `1B, 2C, 4A` |
| 1 from B | 3 from B | `[1,1]` | `2C, 3B, 4A` |
| 2 from C | 6 from C | `[1,1,2]` | `3B, 4A, 6C` |
| 3 from B | 4 from B | `[1,1,2,3]` | `4A, 4B, 6C` |

Continue until output is `[1,1,2,3,4,4,5,6]`.

## Language-neutral pseudocode

```text
heap = empty min_heap ordered by value
for each list_id, head in lists:
    if head is not null:
        heap.push((head.value, list_id, head))

dummy = new output_head
tail = dummy
while heap not empty:
    value, list_id, node = heap.pop_min()
    tail.next = node
    tail = tail.next
    if node.next is not null:
        heap.push((node.next.value, list_id, node.next))
return dummy.next
```

## Complexity proof

Let `N` be the total number of elements and `k` be the number of lists. Each element is pushed and popped once, and the heap contains at most `k` entries. Time is `O(N log k)`. Extra heap space is `O(k)`, plus output storage if new nodes are allocated.

## Scoring rubric

| Dimension | Strong answer |
|---|---|
| Heap entry | Stores value, source id, and node or index |
| Active heads | Keeps only one entry per non-empty source |
| Duplicates | Handles equal values with a tie-breaker if needed |
| Mutation | Clarifies reuse versus copy |
| Complexity | Uses total elements `N` and list count `k` |

## Common pitfalls

1. Pushing all nodes into the heap and losing the `O(log k)` benefit.
2. Failing on empty input lists.
3. Comparing linked-list node objects directly when values tie.
4. Losing the next pointer before appending a node.
5. Creating cycles when reusing nodes without detaching carefully.

## Follow-up questions

1. How would divide-and-conquer merging compare?
2. What changes for sorted arrays instead of linked lists?
3. How would you merge remote sorted feeds with backpressure?
4. How would you handle duplicate suppression?

## Variants and extensions

- Merge sorted log streams.
- Merge ranked search shards.
- Smallest range covering k lists.
- External merge sort.

## Cross-links

- [Heap / Priority Queue Overview](./01-overview.md)
- [Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
- [News Feed HLD](../../04-hld-projects/news-feed/)
