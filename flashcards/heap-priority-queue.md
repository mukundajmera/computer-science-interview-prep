# Heap / Priority Queue Flashcards

> 40 question-only flashcards for heap recognition, priority invariants, top-k, k-way merge, streaming medians, cooldown scheduling, and system-design transfer.

## Foundations

### Card 1
**Front:** What problem shape suggests using a heap?

### Card 2
**Front:** What does a heap guarantee, and what does it not guarantee?

### Card 3
**Front:** Why is heap array order not sorted order?

### Card 4
**Front:** What fields should you define for every heap entry?

### Card 5
**Front:** When is a single full sort better than a heap?

### Card 6
**Front:** How do you simulate a max-heap in a min-heap-only language?

### Card 7
**Front:** Why does heap complexity depend on the heap size, not always on input size?

### Card 8
**Front:** What is lazy deletion in heap problems?

### Card 9
**Front:** When might a balanced tree beat a heap?

### Card 10
**Front:** What should you clarify about ties in heap outputs?

## Core Patterns

### Card 11
**Front:** What is the invariant for kth largest with a size-k min-heap?

### Card 12
**Front:** Why is the root of a size-k min-heap the kth largest value?

### Card 13
**Front:** How do duplicates affect kth largest?

### Card 14
**Front:** What is the first step in Top K Frequent Elements?

### Card 15
**Front:** What does the root mean in a top-k frequent min-heap?

### Card 16
**Front:** Why might bucket sort solve top-k frequent elements?

### Card 17
**Front:** What is the invariant for Merge K Sorted Lists?

### Card 18
**Front:** Why should k-way merge store only one active head per list?

### Card 19
**Front:** What tie-breaker issue appears when heap entries contain linked-list nodes?

### Card 20
**Front:** What are the two heaps in Find Median from Data Stream?

## Edge Cases and Follow-Ups

### Card 21
**Front:** What two invariants must streaming median preserve?

### Card 22
**Front:** How do you compute the median when both heaps have equal size?

### Card 23
**Front:** What changes for sliding-window median?

### Card 24
**Front:** What does Task Scheduler store outside the max-heap?

### Card 25
**Front:** Why can Task Scheduler need idle intervals?

### Card 26
**Front:** What is the common release-time formula after running a task with cooldown `n`?

### Card 27
**Front:** What is the impossibility bound for Reorganize String?

### Card 28
**Front:** Why hold back the previous character in Reorganize String?

### Card 29
**Front:** Why does K Closest Points use squared distance?

### Card 30
**Front:** Why does K Closest Points use a max-heap of size `k`?

## System Design Transfer

### Card 31
**Front:** How does k-way merge map to search or feed systems?

### Card 32
**Front:** How does top-k map to metrics and logging systems?

### Card 33
**Front:** What is a heavy hitter?

### Card 34
**Front:** When would approximate heavy hitter algorithms replace exact heaps?

### Card 35
**Front:** What production risk appears in priority queue schedulers?

### Card 36
**Front:** What metrics validate a priority scheduler?

### Card 37
**Front:** How does cooldown scheduling map to rate limiting or retries?

### Card 38
**Front:** How would you merge local shard top-k results globally?

### Card 39
**Front:** What is the risk of stale heap entries in production systems?

### Card 40
**Front:** Give a concise interview wrap-up for any heap / priority queue problem.
