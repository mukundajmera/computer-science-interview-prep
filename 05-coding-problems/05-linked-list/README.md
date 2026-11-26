# Pattern 05: Linked List

## Theory
A linked list is a linear data structure where elements are not stored at contiguous memory locations. The elements are linked using pointers.

```mermaid
graph LR
    A[Node 1] --> B[Node 2]
    B --> C[Node 3]
    C --> D[Node 4]
    D --> null
```

## System Design Relevance
| Concept | Relevance |
| --- | --- |
| LRU Cache | A combination of a hash map and a doubly linked list is commonly used to implement LRU caches. See [Caching](../../03-hld-concepts/caching) for more details. |
