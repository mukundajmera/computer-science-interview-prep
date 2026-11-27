# Problems

## 1. Reverse Linked List

**Summary:** Reverse the direction of a singly linked list.
**Practice:** [lc-0206-reverse-linked-list](../problem-bank/lc-0206-reverse-linked-list/README.md)

- **Hints:** 
    1. You need to keep track of the previous node.
    2. Iterate through the list and change the `next` pointer of the current node to point to the previous node.
    3. Make sure you don't lose the reference to the rest of the list.
- **Complexity:** Time: O(N), Space: O(1).

## 2. Linked List Cycle

**Summary:** Decide whether following next pointers in a linked list ever loops back.
**Practice:** [lc-0141-linked-list-cycle](../problem-bank/lc-0141-linked-list-cycle/README.md)

- **Hints:**
    1. Can you use two pointers?
    2. Try moving one pointer faster than the other.
    3. If there is a cycle, the faster pointer will eventually catch up to the slower pointer.
- **Complexity:** Time: O(N), Space: O(1).

## 3. Merge Two Sorted Lists

**Summary:** Splice two sorted linked lists together into one sorted list.
**Practice:** [lc-0021-merge-two-sorted-lists](../problem-bank/lc-0021-merge-two-sorted-lists/README.md)

- **Hints:**
    1. Create a dummy node to act as the head of the new list.
    2. Compare the values of the two lists and attach the smaller value to the new list.
    3. If one list is exhausted, attach the rest of the other list to the new list.
- **Complexity:** Time: O(N + M), Space: O(1).

## 4. Middle of the Linked List

**Summary:** Return the middle node of a linked list, choosing the second middle when the length is even.
**Practice:** [lc-0876-middle-of-the-linked-list](../problem-bank/lc-0876-middle-of-the-linked-list/README.md)

- **Hints:**
    1. Can you use two pointers?
    2. Try moving one pointer twice as fast as the other.
    3. When the fast pointer reaches the end, the slow pointer will be at the middle.
- **Complexity:** Time: O(N), Space: O(1).

## 5. Remove Nth Node From End of List

**Summary:** Delete the node that is n positions from the tail of a linked list in a single pass.
**Practice:** [lc-0019-remove-nth-node-from-end-of-list](../problem-bank/lc-0019-remove-nth-node-from-end-of-list/README.md)

- **Hints:**
    1. Can you use two pointers?
    2. Move the fast pointer `n` steps ahead of the slow pointer.
    3. When the fast pointer reaches the end, the slow pointer will be right before the node to be removed.
- **Complexity:** Time: O(N), Space: O(1).

## 6. Palindrome Linked List

**Summary:** Decide whether the values of a linked list read the same forwards and backwards.
**Practice:** [lc-0234-palindrome-linked-list](../problem-bank/lc-0234-palindrome-linked-list/README.md)

- **Hints:**
    1. Can you find the middle of the linked list?
    2. Can you reverse the second half of the linked list?
    3. Compare the first half and the reversed second half.
- **Complexity:** Time: O(N), Space: O(1).

## 7. Intersection of Two Linked Lists

**Summary:** Two singly linked lists may share a tail; find the node where they first meet.

- **Hints:**
    1. Can you use two pointers?
    2. When a pointer reaches the end of its list, redirect it to the head of the other list.
    3. If they intersect, they will eventually meet at the intersection point.
- **Complexity:** Time: O(N + M), Space: O(1).

## 8. LRU Cache

**Summary:** Design a fixed-capacity cache that evicts the least recently used entry, with constant-time get and put.
**Practice:** [lc-0146-lru-cache](../problem-bank/lc-0146-lru-cache/README.md)

- **Hints:**
    1. You need a data structure that supports fast insertions, deletions, and lookups.
    2. A combination of a hash map and a doubly linked list is commonly used to implement LRU caches.
    3. The hash map will store the keys and the corresponding nodes in the doubly linked list.
- **Complexity:** Time: O(1) for both `get` and `put`, Space: O(capacity).
