# Intervals and Sweep-line Quiz

**Difficulty:** Advanced | **Time:** 45 minutes

20 coding-pattern questions for Merge Intervals, Meeting Rooms II, Non-overlapping Intervals, and Sweep-line calendar bookings.

### Question 1
What is the standard first step for most Interval problems like 'Merge Intervals'?
- **A)** Insert all intervals into a Min-Heap.
- **B)** Sort the intervals based on their end times.
- **C)** Sort the intervals based on their start times.
- **D)** Use a two-pointer approach from both ends of the list.

### Question 2
In 'Merge Intervals', after sorting by start time, when do two adjacent intervals [s1, e1] and [s2, e2] overlap?
- **A)** When s2 <= e1.
- **B)** When e2 > s1.
- **C)** When s2 < e1.
- **D)** When s2 >= e1.

### Question 3
For 'Meeting Rooms II' (finding minimum rooms required), what is the optimal Sweep-line approach?
- **A)** Merge all overlapping intervals and count the merged result.
- **B)** Sort intervals by end time and greedily pick non-overlapping ones.
- **C)** Use a Stack to keep track of the current room.
- **D)** Separate start and end times into events, sort them, and iterate while keeping a running count of active meetings (+1 for start, -1 for end).

### Question 4
In the Sweep-line approach for 'Meeting Rooms II', if a start event and an end event occur at the exact same time, which should be processed first to minimize rooms?
- **A)** The end event should be processed first.
- **B)** They must be merged into a single event.
- **C)** The start event should be processed first.
- **D)** It doesn't matter; the result is the same.

### Question 5
What is the core greedy strategy for 'Non-overlapping Intervals' (finding minimum removals to make intervals non-overlapping)?
- **A)** Merge all intervals and count the overlaps.
- **B)** Sort by end time and always pick the interval that ends earliest to leave maximum room for future intervals.
- **C)** Sort by start time and pick the shortest interval.
- **D)** Sort by duration and pick the shortest intervals first.

### Question 6
How does 'Insert Interval' differ optimally from 'Merge Intervals'?
- **A)** Since the list is already sorted, it can be done in O(N) time by finding the insertion point and merging only affected intervals.
- **B)** It cannot be done faster than O(N log N).
- **C)** It uses a Segment Tree to update the intervals.
- **D)** It requires an O(N log N) re-sort of the entire list.

### Question 7
In 'Interval List Intersections' involving two sorted lists of disjoint intervals, what pattern is most effective?
- **A)** A sweep-line algorithm with a priority queue.
- **B)** A monotonic stack.
- **C)** Concatenating both lists and sorting them.
- **D)** A two-pointer approach comparing the current interval from both lists.

### Question 8
When implementing 'My Calendar I' (preventing any double booking), what data structure allows optimal O(log N) booking?
- **A)** A Min-Heap.
- **B)** A balanced Binary Search Tree (like a TreeMap in Java).
- **C)** A standard unsorted array.
- **D)** A Hash Map with start times as keys.

### Question 9
For 'My Calendar II' (allowing double bookings but preventing triple bookings), how can this be managed?
- **A)** Use a single boolean array representing time slots.
- **B)** Just use the Sweep-line algorithm every time a booking is made.
- **C)** Maintain a list of single bookings and a list of double booked overlapping regions; check against the double booked list first.
- **D)** It requires a Segment Tree with lazy propagation.

### Question 10
In 'My Calendar III' (finding the maximum number of concurrent bookings), which approach is highly effective?
- **A)** Merging all intervals and returning the size of the array.
- **B)** A boundary count (Sweep-line) using a TreeMap to keep events sorted, updating counts and finding the max prefix sum.
- **C)** Sorting by end times and applying a greedy approach.
- **D)** A BFS traversal of the interval graph.

### Question 11
The 'Skyline Problem' is a classic sweep-line problem. What additional data structure is typically used with the sweep-line?
- **A)** A Max-Heap (or TreeMap) to keep track of the current highest active building.
- **B)** A Disjoint Set Union.
- **C)** A Monotonic Deque.
- **D)** A Trie.

### Question 12
In the 'Skyline Problem', what constitutes a critical point that needs to be added to the result?
- **A)** Every building's start and end coordinate.
- **B)** Only the start coordinates of buildings.
- **C)** When processing an event changes the maximum height currently active.
- **D)** Where two buildings intersect.

### Question 13
What is the time complexity of the standard sorting-based Sweep-line algorithm for N intervals?
- **A)** O(N)
- **B)** O(log N)
- **C)** O(N log N)
- **D)** O(N^2)

### Question 14
For 'Minimum Number of Arrows to Burst Balloons', what is the optimal sorting strategy?
- **A)** Sort by diameter of the balloon.
- **B)** Sort randomly and use a greedy approach.
- **C)** Sort by start coordinates; shoot an arrow at the start of the balloon.
- **D)** Sort by end coordinates; shoot an arrow at the end of the current balloon to burst as many overlapping ones as possible.

### Question 15
How can 'Employee Free Time' (finding common free time for all employees given their schedules) be solved?
- **A)** Merge all employee intervals into a single sorted list, then find the gaps between merged intervals.
- **B)** Use a Min-Heap to process all intervals simultaneously without merging.
- **C)** Use a Segment Tree to query free slots.
- **D)** Find the intersection of all intervals.

### Question 16
In 'Data Stream as Disjoint Intervals', what is the challenge of adding numbers one by one?
- **A)** Keeping the stream sorted.
- **B)** Calculating the average of the intervals.
- **C)** Efficiently merging the new number with existing adjacent intervals (e.g., [1,1] and [3,3] become [1,3] when 2 is added).
- **D)** Handling duplicate numbers gracefully.

### Question 17
What data structure is ideal for 'Data Stream as Disjoint Intervals' in languages that support it?
- **A)** A hash set.
- **B)** A self-balancing BST (like TreeMap/std::set) to easily find predecessor and successor intervals.
- **C)** A monotonic stack.
- **D)** A standard queue.

### Question 18
In 'Maximum CPU Load', which is synonymous with Meeting Rooms II, what are we tracking during the sweep-line?
- **A)** The number of concurrent jobs, ignoring their specific load weights.
- **B)** The job with the highest individual CPU load.
- **C)** The total duration of all jobs.
- **D)** The sum of CPU loads for all active jobs at any point in time, updating the maximum seen so far.

### Question 19
What is a common edge case to handle when merging intervals?
- **A)** Empty interval lists.
- **B)** An interval that is completely engulfed by another (e.g., [1, 5] and [2, 3]).
- **C)** Intervals that start at 0.
- **D)** Intervals that have negative start times.

### Question 20
Why is sorting by end time often better than start time for greedy interval selection (like Non-overlapping Intervals)?
- **A)** It prevents the need to check for overlaps entirely.
- **B)** It inherently handles negative numbers better.
- **C)** It is computationally faster to sort by end time.
- **D)** It guarantees that the selected interval finishes as early as possible, leaving the maximum contiguous space for subsequent intervals.
