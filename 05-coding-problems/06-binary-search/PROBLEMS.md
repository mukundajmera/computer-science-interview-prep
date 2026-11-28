# PROBLEMS.md

## Problem 1: Classic Binary Search

**Summary:** Search a sorted array for a target value and report its index, or a sentinel when it is absent.

Hints:
1. Initialize left and right pointers.
2. Find the midpoint.
3. Eliminate half the space.
Complexity: O(log n) time, O(1) space.

## Problem 2: First Position / Lower Bound

**Summary:** In a sorted array that may repeat values, find the first index whose value is at least the target.

Hints:
1. Use half-open search range.
2. Predicate: `nums[mid] >= target`.
3. Don't return early.
Complexity: O(log n) time, O(1) space.

## Problem 3: Search Insert Position

**Summary:** In a sorted array, find the index of a target or where it would be inserted.
**Practice:** [lc-0035-search-insert-position](../problem-bank/lc-0035-search-insert-position/README.md)

Hints:
1. This is lower bound.
2. Return left pointer.
3. Don't return -1.
Complexity: O(log n) time, O(1) space.

## Problem 4: Search in Rotated Sorted Array

**Summary:** Find a target in a sorted array that has been rotated at an unknown pivot, in logarithmic time.
**Practice:** [lc-0033-search-in-rotated-sorted-array](../problem-bank/lc-0033-search-in-rotated-sorted-array/README.md)

Hints:
1. One half is always sorted.
2. Check if target is in the sorted half.
3. Update pointers accordingly.
Complexity: O(log n) time, O(1) space.

## Problem 5: Find Minimum in Rotated Sorted Array

**Summary:** A sorted array of distinct values was rotated; locate its smallest element faster than a full scan.
**Practice:** [lc-0153-find-minimum-in-rotated-sorted-array](../problem-bank/lc-0153-find-minimum-in-rotated-sorted-array/README.md)

Hints:
1. Compare mid with right pointer.
2. If mid > right, min is to the right.
3. If mid <= right, min is at or to the left of mid.
Complexity: O(log n) time, O(1) space.

## Problem 6: Koko Eating Bananas

**Summary:** Find the smallest constant eating speed that finishes all piles within a time limit.

Hints:
1. Binary search on the answer (speed).
2. Speed range is 1 to max(piles).
3. Monotonic predicate: can Koko eat all bananas at speed k within h hours?
Complexity: O(n log(max_pile)) time, O(1) space.

## Problem 7: Search a 2D Matrix

**Summary:** Search for a value in a matrix whose rows are sorted and each row continues from the previous one.
**Practice:** [lc-0074-search-a-2d-matrix](../problem-bank/lc-0074-search-a-2d-matrix/README.md)

Hints:
1. Treat matrix as 1D array.
2. Map 1D index to 2D coordinates.
3. Perform standard binary search.
Complexity: O(log(m*n)) time, O(1) space.
