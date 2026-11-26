# Interval Problems

## 1. Merge Intervals

**Summary:** Combine all overlapping ranges in a list into the smallest set of disjoint ranges.
**Practice:** [lc-0056-merge-intervals](problem-bank/lc-0056-merge-intervals/README.md)

- **Hints**:
  1. Sort the intervals by their start times.
  2. If the current interval overlaps with the previous one, merge them by updating the end time of the previous interval to the maximum of both end times.
  3. Otherwise, just add the current interval to the result.
- **Complexity**: Time O(N log N) for sorting, Space O(N) or O(log N) for sorting depending on language implementation.

## 2. Insert Interval

**Summary:** Add a new interval into a sorted list of non-overlapping intervals, merging anything that overlaps.
**Practice:** [lc-0057-insert-interval](problem-bank/lc-0057-insert-interval/README.md)

- **Hints**:
  1. Find all intervals ending before `newInterval` starts and add them directly.
  2. Merge all overlapping intervals into `newInterval`.
  3. Add the rest of the intervals.
- **Complexity**: Time O(N) since input is sorted, Space O(N) for output array.

## 3. Non-overlapping Intervals

**Summary:** Find the fewest intervals to remove so that the rest do not overlap.
**Practice:** [lc-0435-non-overlapping-intervals](problem-bank/lc-0435-non-overlapping-intervals/README.md)

- **Hints**:
  1. This is a classic greedy problem.
  2. Sort the intervals by their end times.
  3. Keep track of the end time of the last added interval. If the next interval starts before this end time, it overlaps and must be removed.
- **Complexity**: Time O(N log N) for sorting, Space O(log N) or O(N) for sorting.

## 4. Meeting Rooms

**Summary:** Given meeting time ranges, decide whether one person could attend all of them.
**Practice:** [lc-0252-meeting-rooms](problem-bank/lc-0252-meeting-rooms/README.md)

- **Hints**:
  1. Sort intervals by start time.
  2. Check if any adjacent intervals overlap.
  3. Return false if overlap is found, else true.
- **Complexity**: Time O(N log N), Space O(log N) for sorting.

## 5. Meeting Rooms II

**Summary:** Given meeting time ranges, find the minimum number of rooms needed so none overlap in a room.
**Practice:** [lc-0253-meeting-rooms-ii](problem-bank/lc-0253-meeting-rooms-ii/README.md)

- **Hints**:
  1. You can use a min-heap to track end times of meetings.
  2. Or, sort start times and end times separately, then use two pointers to iterate through them.
  3. Keep a running count of active rooms.
- **Complexity**: Time O(N log N), Space O(N).

## 6. Minimum Number of Arrows to Burst Balloons

**Summary:** Balloons occupy horizontal ranges; find the fewest vertical shots that pop them all.
**Practice:** [lc-0452-minimum-number-of-arrows-to-burst-balloons](problem-bank/lc-0452-minimum-number-of-arrows-to-burst-balloons/README.md)

- **Hints**:
  1. Sort balloons by their end coordinate.
  2. Shoot an arrow at the end of the current balloon to burst as many subsequent balloons as possible.
  3. If a balloon starts after the current arrow, you need a new arrow.
- **Complexity**: Time O(N log N), Space O(log N) or O(N) for sorting.

## 7. Interval List Intersections

**Summary:** Given two sorted lists of disjoint intervals, return the overlaps between them.

- **Hints**:
  1. Use two pointers, one for each list.
  2. Find the overlap between the current intervals (max of starts, min of ends).
  3. Advance the pointer of the interval that ends first.
- **Complexity**: Time O(M + N), Space O(M + N) for output.
