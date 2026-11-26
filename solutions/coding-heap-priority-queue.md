# Coach Answer: Coding Heap / Priority Queue Pack

> Type: Coding Pattern Drill
> Difficulty: Intermediate
> Time Target: 45 minutes

## Phase 1 - Problem Framing

Strong candidates do not say "use a priority queue" and stop. They define the frontier.

1. Identify the repeated priority decision: minimum, maximum, kth boundary, most frequent, closest, or next available.
2. Define the heap entry: priority fields plus value, source id, index, count, or release time.
3. Choose heap direction: min-heap, max-heap, size-k heap, or two heaps.
4. State the invariant: what the root means after each operation.
5. Bound the heap size: `k`, number of lists, unique labels, or all values.
6. Handle ties and invalid inputs explicitly; include scalar tie-breakers when heap entries contain objects.
7. Separate heap order from sorted output.

## Phase 2 - Canonical Templates

### Template A: Size-K Min-Heap for Kth Largest

```text
heap = min_heap
for value in values:
    heap.push(value)
    if heap.size > k:
        heap.pop_min()
return heap.peek_min()
```

Use when the root should be the weakest kept winner.

### Template B: Top K by Frequency

```text
counts = frequency_map(values)
heap = min_heap ordered by count
for value, count in counts:
    heap.push((count, value))
    if heap.size > k:
        heap.pop_min()
return values from heap
```

Use when counting is mandatory before ranking.

### Template C: K-Way Merge

```text
heap = min_heap ordered by value
for source in sources:
    if source has first item:
        heap.push((first.value, source.id, first))

while heap not empty:
    value, source_id, item = heap.pop_min()
    emit item
    if item has next in same source:
        heap.push((next.value, source_id, next))
```

Use when each source is already sorted.

### Template D: Two Heaps for Median

```text
lower = max_heap
upper = min_heap

add(x):
    push x into the correct half
    rebalance until sizes differ by at most one

median():
    if one heap is larger: return its root
    return average(lower.root, upper.root)
```

The ordering invariant is as important as the size invariant.

### Template E: Max-Heap with Cooldown

```text
heap = max_heap of available counts
cooldown = queue of (ready_time, count)
time = 0
while heap or cooldown:
    time += 1
    release ready cooldown entries back to heap
    if heap:
        count = heap.pop_max() - 1
        if count > 0:
            cooldown.push((time + cooldown_gap + 1, count))
return time
```

Use when the best item cannot be reused immediately.

### Template F: Size-K Max-Heap for Closest Items

```text
heap = max_heap ordered by distance
for stable_id, item in enumerate(items):
    heap.push((distance(item), stable_id, item))
    if heap.size > k:
        heap.pop_max()
return items from heap
```

Use when you keep the closest `k` and evict the farthest kept candidate.

If tied outputs may be arbitrary, say so. If output must be deterministic, use a stable scalar tie-breaker such as input index, not raw object comparison.

## Phase 3 - Problem-by-Problem Walkthrough

1. **Top K Frequent Elements**
   - State: frequency map plus min-heap of size `k`.
   - Root: least frequent kept candidate.

2. **Kth Largest Element**
   - State: min-heap containing the `k` largest values seen so far.
   - Root: kth largest after all values are scanned.

3. **Merge K Sorted Lists**
   - State: one active head per sorted source.
   - Root: next globally smallest output value.

4. **Find Median from Data Stream**
   - State: lower max-heap and upper min-heap.
   - Invariants: ordered halves and balanced sizes.

5. **Task Scheduler**
   - State: max-heap of available task counts plus cooldown queue.
   - Root: highest remaining available task.

6. **Reorganize String**
   - State: max-heap of eligible characters plus held previous character.
   - Guardrail: max frequency cannot exceed `(n + 1) / 2`.

7. **K Closest Points**
   - State: max-heap of size `k` ordered by squared distance.
   - Root: farthest among the kept closest points.

## Phase 4 - Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Frontier definition | 25% | Defines heap entries and root meaning |
| Invariant quality | 25% | Explains why each push/pop preserves correctness |
| Size bound | 15% | Uses `log k`, `log U`, or `log lists` correctly |
| Edge cases | 15% | Handles empty input, ties, duplicates, invalid `k`, impossible schedules |
| Complexity | 10% | Separates counting, heap updates, and output sorting |
| Communication | 10% | Contrasts heap with sorting, quickselect, or trees when relevant |

## Phase 5 - Common Pitfalls

1. Returning heap internal array order as sorted output.
2. Using the wrong heap direction for closest or largest problems.
3. Forgetting tie-breakers for custom heap entries.
4. Letting bounded top-k heaps grow to all input values.
5. Reusing a cooled-down task or previous character too soon.
6. Balancing median heaps by size but breaking lower <= upper ordering.
7. Ignoring duplicates in kth largest.
8. Hiding stale entries instead of discarding them when popped.

## System Design Transfer Script

| Heap concept | Production analogue | Scale risk | Validation signal |
|---|---|---|---|
| Top-k frontier | heavy hitters, trending items | missing long-tail bursts | recall audit, sampled exact comparison |
| K-way merge | search shards, feed fan-in, log streams | slow shard blocks output | shard latency, backpressure, timeout rate |
| Two heaps | running median or percentile view | memory growth, skewed streams | quantile error, heap size, freshness |
| Cooldown queue | retry throttling, rate limits | starvation, unfairness | queue age, retry success, tenant fairness |
| Priority scheduler | job dispatch by urgency | priority inversion | deadline misses, starvation, preemption count |

## Follow-Up Drill Set

1. Sliding Window Median.
2. Kth Largest in a Stream.
3. Meeting Rooms II.
4. Smallest Range Covering K Lists.
5. Find K Pairs with Smallest Sums.
6. IPO / maximize capital.
7. Twitter feed fan-in.
8. Top K Frequent Words with lexicographic tie-break.

## Cross-links

- [Heap / Priority Queue Pattern Pack](../05-coding-problems/heap-priority-queue/README.md)
- [Heap / Priority Queue Quiz](../quizzes/heap-priority-queue-quiz.md)
- [Heap / Priority Queue Flashcards](../flashcards/heap-priority-queue.md)
- [Job Scheduler HLD](../04-hld-projects/job-scheduler/)
- [News Feed HLD](../04-hld-projects/news-feed/)
