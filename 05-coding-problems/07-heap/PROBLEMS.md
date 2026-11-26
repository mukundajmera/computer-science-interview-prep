# Heap / Priority Queue Problems

## 1. Top K Frequent Elements

**Summary:** Return the k values that occur most often in an array.

- **Hints:** 
  1. Use a hash map to count frequencies.
  2. Use a min-heap of size k to keep the top elements.
  3. Push elements into the heap, pop if size > k.
- **Complexity:** O(N log K) time, O(N) space.

## 2. Merge K Sorted Lists

**Summary:** Combine several sorted linked lists into a single sorted list.
**Practice:** [lc-0023-merge-k-sorted-lists](problem-bank/lc-0023-merge-k-sorted-lists/README.md)

- **Hints:**
  1. Use a min-heap to keep track of the smallest node among the k lists.
  2. Push the head of each list into the heap.
  3. Pop the smallest, and push its next node.
- **Complexity:** O(N log K) time, O(K) space.

## 3. Find Median from Data Stream

**Summary:** Support adding numbers one at a time while being able to report the current median at any moment.
**Practice:** [lc-0295-find-median-from-data-stream](problem-bank/lc-0295-find-median-from-data-stream/README.md)

- **Hints:**
  1. Use two heaps: a max-heap for the lower half and a min-heap for the upper half.
  2. Keep the sizes balanced or max-heap one larger.
  3. The median is either the top of the max-heap or the average of the tops.
- **Complexity:** O(log N) add, O(1) find, O(N) space.

## 4. Task Scheduler

**Summary:** Tasks of various types must wait a cooldown between repeats of the same type; find the shortest total time to finish them.
**Practice:** [lc-0621-task-scheduler](problem-bank/lc-0621-task-scheduler/README.md)

- **Hints:**
  1. Count frequencies of tasks.
  2. Use a max-heap to pick the most frequent task available.
  3. Use a queue to handle the cooldown.
- **Complexity:** O(N) time, O(1) space (26 chars).

## 5. Kth Largest Element in an Array

**Summary:** Return the element that would be kth from the top if the array were sorted.
**Practice:** [lc-0215-kth-largest-element-in-an-array](problem-bank/lc-0215-kth-largest-element-in-an-array/README.md)

- **Hints:**
  1. Use a min-heap of size k.
  2. Add elements, if size exceeds k, pop the minimum.
  3. The top of the heap is the kth largest.
- **Complexity:** O(N log K) time, O(K) space.

## 6. K Closest Points to Origin

**Summary:** From a list of 2D points, return the k that lie nearest to the origin.
**Practice:** [lc-0973-k-closest-points-to-origin](problem-bank/lc-0973-k-closest-points-to-origin/README.md)

- **Hints:**
  1. Calculate squared distance for each point.
  2. Use a max-heap of size k to store the closest points.
  3. Keep popping the farthest if size exceeds k.
- **Complexity:** O(N log K) time, O(K) space.

## 7. Cheapest Flights Within K Stops

**Summary:** Find the cheapest route between two cities that uses at most a given number of intermediate stops.
**Practice:** [lc-0787-cheapest-flights-within-k-stops](problem-bank/lc-0787-cheapest-flights-within-k-stops/README.md)

- **Hints:**
  1. Use a modified Dijkstra's with a priority queue.
  2. State in PQ: `(cost, node, stops_remaining)`.
  3. Prune if a node has been visited with fewer stops and lower cost.
- **Complexity:** O(E + V log V) time.
