# Remove Duplicates From Sorted List

- Canonical ID: `lc-0083-remove-duplicates-from-sorted-list`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Given the head of a sorted linked list, collapse each run of equal values to a single node and return the head of the deduplicated list.

## Driver Signature

- Java: `ListNode deleteDuplicates(ListNode head)`
- Python: `deleteDuplicates(head: Optional[ListNode]) -> Optional[ListNode]`

## Key Cases and Invariants

- Sorted order means duplicates are adjacent.
- An empty list and a single-node list are already deduplicated.

## Solution Ladder

### Tier 1: Build a new unique list

Collect the first value of each sorted run, then build a fresh linked list from those values.

- Time: `O(n)` - The list is traversed once and a new node is built for each unique value.
- Space: `O(u)` - `u` unique values are stored and rebuilt.

### Tier 2: In-place run skipping

Walk the list and bypass the next node whenever it has the same value as the current node.

- Time: `O(n)` - Each node is inspected at most once.
- Space: `O(1)` - The algorithm rewires existing `next` pointers without auxiliary collections.
