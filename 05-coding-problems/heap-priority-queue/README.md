# Heap / Priority Queue Pattern Pack

A focused coding pattern pack for problems where the next item must be chosen by priority: top-k selection, streaming medians, k-way merge, closest points, delayed scheduling, and frequency-driven rearrangement.

## Overview

A heap is not just a faster sort. It is a way to keep only the best boundary items visible.

Use a heap when the problem repeatedly asks for the minimum, maximum, kth boundary, or next best candidate while the full input changes or is too large to sort repeatedly. The interview signal is knowing what the heap stores, what comparator or priority orders it, how tie-breaking should behave, and why the heap size stays bounded.

Common patterns:

1. Use a min-heap of size `k` to keep the `k` largest items.
2. Use a max-heap to repeatedly take the most frequent or most urgent item.
3. Use two heaps to maintain a lower half and upper half in a stream.
4. Use a heap of heads to merge many sorted sources.
5. Use priority plus cooldown or delayed reinsert when an item cannot be reused immediately.

## When to Use

Use heap / priority queue when the problem gives you:

1. "Top k", "kth largest", "k closest", or "k smallest".
2. A stream where sorting after every insertion is too expensive.
3. Multiple sorted lists or feeds that need one globally sorted output.
4. Repeated scheduling by next available time, highest frequency, or earliest deadline.
5. A local best item that must be updated after each choice.

Strong recognition cues:

- "return the kth largest"
- "find top k frequent"
- "merge k sorted lists"
- "median from a data stream"
- "least intervals with cooldown"
- "reorganize so adjacent characters differ"
- "k closest points to origin"

## When Not to Use

Avoid heap / priority queue when:

1. A single full sort is simpler and within the target complexity.
2. You need exact order of all results and sorting is not repeated.
3. The problem needs range queries, predecessor/successor lookup, or arbitrary deletion. A balanced tree or indexed structure may fit better.
4. The objective depends on future combinations, not only the next priority item.
5. The required priority changes for many existing elements and the language heap cannot update keys cleanly.

The common warning: using a heap can hide an `O(n log n)` sort behind more complicated code. Prefer the heap only when bounded size, streaming, or incremental priority matters.

## Pattern Taxonomy

| Variant | Best fit | Key invariant |
|---|---|---|
| Size-k min-heap | kth largest, top k largest | heap contains the best `k` items seen so far |
| Frequency heap | top frequent, reorganize string | heap exposes the largest remaining count |
| Two heaps | streaming median | lower half and upper half are balanced and ordered |
| K-way merge heap | merge sorted lists, feeds | heap contains the current head from each active source |
| Distance heap | k closest points | heap keeps the closest boundary by distance |
| Heap plus cooldown | task scheduler, no adjacent reuse | unavailable items wait until they can be chosen again |
| Lazy deletion heap | sliding priorities with stale entries | stale heap entries are discarded when popped |

## Common Failure Modes

1. Forgetting whether the language heap is min-first or max-first.
2. Letting a top-k heap grow to `n` when it should stay at size `k`.
3. Returning heap order as sorted order without popping or sorting the final heap.
4. Recomputing frequencies or distances inside comparisons more than needed.
5. Mutating linked-list nodes in k-way merge without preserving the next pointer.
6. Reusing the same task or character before cooldown or adjacency rules allow it.
7. Misbalancing two heaps and returning the wrong median for even counts.
8. Ignoring tie-breaking rules when deterministic output is expected.

## Interview Scoring Focus

| Dimension | Strong signal |
|---|---|
| Heap contents | States exactly what each heap entry stores |
| Priority key | Names min, max, frequency, distance, value, next time, and the comparator/tie-breaking policy |
| Bounded size | Explains why heap size is `k`, number of lists, or alphabet size |
| Invariant | Keeps ordering and balance conditions explicit |
| Edge cases | Handles empty input, `k` limits, ties, duplicates, and impossible schedules |
| Complexity | Separates build, push/pop cost, and output cost |

## 60-90 Second Answer

Say:

"I use a heap when I only need the next best item or a bounded top-k frontier, not a full sorted order after every update. I will define the heap entry and priority first. For kth largest, I keep a min-heap of size `k`, so the root is the kth largest among values seen so far. For streaming median, I keep a max-heap for the lower half and a min-heap for the upper half, with sizes differing by at most one. For k-way merge, the heap stores one current node per list, so each output pop is globally smallest among active heads. The invariant is what makes the complexity `O(n log k)` or `O(log n)` per update instead of repeated sorting."

## Problem Track

1. [01-overview.md](./01-overview.md)
2. [02-top-k-frequent-elements.md](./02-top-k-frequent-elements.md)
3. [03-kth-largest-element.md](./03-kth-largest-element.md)
4. [04-merge-k-sorted-lists.md](./04-merge-k-sorted-lists.md)
5. [05-find-median-from-data-stream.md](./05-find-median-from-data-stream.md)
6. [06-task-scheduler.md](./06-task-scheduler.md)
7. [07-reorganize-string.md](./07-reorganize-string.md)
8. [08-k-closest-points.md](./08-k-closest-points.md)

## Cross-links

- [Common Complexities](../../00-theory/complexity-analysis/common-complexities.md)
- [Pattern to System Design Map](../PATTERN-SD-MAP.md)
- [Job Scheduler HLD](../../04-hld-projects/job-scheduler/)
- [News Feed HLD](../../04-hld-projects/news-feed/)
- [Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
- [Message Queues](../../03-hld-concepts/message-queues/THEORY.md)
- [Heap / Priority Queue Quiz](../../quizzes/heap-priority-queue-quiz.md)
- [Heap / Priority Queue Flashcards](../../flashcards/heap-priority-queue.md)
- [Coach Answer: Coding Heap / Priority Queue](../../solutions/coding-heap-priority-queue.md)
