# 📊 Complexity Reference Cheatsheet

Quick reference for Big-O complexity of common operations.

---

## 🎯 Quick Rules

### Calculating Time Complexity
1. **Drop constants**: O(2n) → O(n)
2. **Drop lower order terms**: O(n² + n) → O(n²)
3. **Nested loops multiply**: Two nested loops of n → O(n²)
4. **Sequential code adds**: O(n) + O(m) = O(n + m)
5. **Different inputs = different variables**: Array of n, Array of m → O(n + m)

### Common Patterns
| Pattern | Complexity | Example |
|---------|------------|---------|
| Single loop | O(n) | Iterate through array |
| Nested loops | O(n²) | Compare all pairs |
| Divide by 2 each step | O(log n) | Binary search |
| Loop + divide | O(n log n) | Merge sort |
| All subsets | O(2ⁿ) | Power set |
| All permutations | O(n!) | Traveling salesman |

---

## 📦 Data Structure Operations

### Arrays

| Operation | Average | Worst | Notes |
|-----------|---------|-------|-------|
| Access by index | O(1) | O(1) | Direct memory access |
| Search (unsorted) | O(n) | O(n) | Linear scan |
| Search (sorted) | O(log n) | O(log n) | Binary search |
| Insert at end | O(1)* | O(n) | *Amortized, resize if needed |
| Insert at beginning | O(n) | O(n) | Shift all elements |
| Insert at middle | O(n) | O(n) | Shift elements |
| Delete at end | O(1) | O(1) | |
| Delete at beginning | O(n) | O(n) | Shift all elements |

**Space Complexity:** O(n)

---

### Linked List

| Operation | Singly | Doubly | Notes |
|-----------|--------|--------|-------|
| Access by index | O(n) | O(n) | Traverse from head |
| Search | O(n) | O(n) | Linear scan |
| Insert at head | O(1) | O(1) | Just update pointers |
| Insert at tail | O(n)/O(1)* | O(1) | *O(1) if tail pointer maintained |
| Insert at middle | O(n) | O(n) | Find position first |
| Delete at head | O(1) | O(1) | |
| Delete at tail | O(n) | O(1) | Doubly linked has prev pointer |
| Delete at middle | O(n) | O(n) | Find position first |

**Space Complexity:** O(n)

---

### Stack & Queue

| Operation | Stack | Queue | Notes |
|-----------|-------|-------|-------|
| Push/Enqueue | O(1) | O(1) | Add to end |
| Pop/Dequeue | O(1) | O(1) | Remove from end/front |
| Peek/Front | O(1) | O(1) | View without remove |
| Search | O(n) | O(n) | Not typical operation |
| isEmpty | O(1) | O(1) | Check size |

**Space Complexity:** O(n)

---

### HashMap / HashTable

| Operation | Average | Worst | Notes |
|-----------|---------|-------|-------|
| Get | O(1) | O(n) | Worst case: all hash collisions |
| Put | O(1) | O(n) | Amortized O(1) with good hash |
| Delete | O(1) | O(n) | |
| ContainsKey | O(1) | O(n) | |
| Keys/Values iteration | O(n) | O(n) | |

**Space Complexity:** O(n)

**Tips:**
- Use when you need O(1) lookup
- Good hash function crucial for performance
- Java: HashMap, Python: dict, JavaScript: Object/Map

---

### TreeMap / BST (Balanced)

| Operation | Average | Worst (Balanced) | Notes |
|-----------|---------|------------------|-------|
| Get | O(log n) | O(log n) | Red-Black, AVL trees |
| Put | O(log n) | O(log n) | Self-balancing |
| Delete | O(log n) | O(log n) | |
| Min/Max | O(log n) | O(log n) | Traverse left/right |
| In-order traversal | O(n) | O(n) | Sorted order |

**Space Complexity:** O(n)

**Use When:**
- Need sorted keys
- Need range queries
- Need floor/ceiling operations

---

### Heap (Priority Queue)

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Insert | O(log n) | Bubble up |
| Extract Min/Max | O(log n) | Bubble down |
| Peek | O(1) | View top element |
| Build Heap | O(n) | From array |
| Heapify | O(log n) | Single element |

**Space Complexity:** O(n)

**Use When:**
- Need quick access to min/max
- K-th largest/smallest problems
- Merge K sorted lists

---

### Trie (Prefix Tree)

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Insert | O(m) | m = word length |
| Search | O(m) | |
| Prefix search | O(m) | |
| Delete | O(m) | |

**Space Complexity:** O(alphabet_size × m × n) where n = number of words

**Use When:**
- Autocomplete
- Spell checker
- IP routing tables

---

### Graph (Adjacency List)

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Add Vertex | O(1) | |
| Add Edge | O(1) | |
| Remove Vertex | O(V + E) | Remove all edges too |
| Remove Edge | O(E) | Find in list |
| Check Edge exists | O(degree) | |
| Get all neighbors | O(degree) | |
| DFS/BFS | O(V + E) | Visit all vertices and edges |

**Space Complexity:** O(V + E)

---

## 🔄 Sorting Algorithms

| Algorithm | Best | Average | Worst | Space | Stable | Notes |
|-----------|------|---------|-------|-------|--------|-------|
| **Quick Sort** | O(n log n) | O(n log n) | O(n²) | O(log n) | No | Pivot choice matters |
| **Merge Sort** | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes | Guaranteed performance |
| **Heap Sort** | O(n log n) | O(n log n) | O(n log n) | O(1) | No | In-place |
| **Tim Sort** | O(n) | O(n log n) | O(n log n) | O(n) | Yes | Python/Java default |
| **Bubble Sort** | O(n) | O(n²) | O(n²) | O(1) | Yes | Never use in practice |
| **Insertion Sort** | O(n) | O(n²) | O(n²) | O(1) | Yes | Good for small/nearly sorted |
| **Selection Sort** | O(n²) | O(n²) | O(n²) | O(1) | No | Never use in practice |
| **Counting Sort** | O(n + k) | O(n + k) | O(n + k) | O(k) | Yes | k = range of input |
| **Radix Sort** | O(nk) | O(nk) | O(nk) | O(n + k) | Yes | k = number of digits |

**When to Use:**
- General purpose → **Quick Sort** or **Merge Sort**
- Guaranteed O(n log n) → **Merge Sort** or **Heap Sort**
- Nearly sorted data → **Insertion Sort** or **Tim Sort**
- Integer range known → **Counting Sort** or **Radix Sort**

---

## 🔍 Algorithm Patterns

### Binary Search

| Variant | Time | Space | Use Case |
|---------|------|-------|----------|
| Standard | O(log n) | O(1) | Find exact element |
| Lower bound | O(log n) | O(1) | First element ≥ target |
| Upper bound | O(log n) | O(1) | First element > target |
| Rotated array | O(log n) | O(1) | Search in rotated sorted array |

---

### Two Pointers

| Technique | Time | Space | Use Case |
|-----------|------|-------|----------|
| Start/End | O(n) | O(1) | Pair sum, Palindrome |
| Same direction | O(n) | O(1) | Remove duplicates |
| Fast/Slow | O(n) | O(1) | Cycle detection |

---

### Sliding Window

| Type | Time | Space | Use Case |
|------|------|-------|----------|
| Fixed size | O(n) | O(1) | Max sum of k elements |
| Variable size | O(n) | O(k) | Longest substring without repeating |

---

### DFS / BFS

| Algorithm | Time | Space | Use Case |
|-----------|------|-------|----------|
| DFS (recursive) | O(V + E) | O(V) | Path finding, Connected components |
| DFS (iterative) | O(V + E) | O(V) | Same, avoids stack overflow |
| BFS | O(V + E) | O(V) | Shortest path (unweighted) |

---

### Dynamic Programming

| Pattern | Time | Space | Example |
|---------|------|-------|---------|
| 1D DP | O(n) | O(n) or O(1) | Fibonacci, Climbing stairs |
| 2D DP | O(n×m) | O(n×m) or O(min(n,m)) | LCS, Edit distance |
| State machine | O(n×k) | O(n×k) | Stock problems |

---

## 📏 Space Complexity Common Patterns

| Pattern | Space | Example |
|---------|-------|---------|
| Fixed variables | O(1) | Counters, pointers |
| Array of size n | O(n) | Copy of input |
| Matrix n×m | O(n×m) | 2D DP table |
| Recursive stack | O(depth) | DFS, divide & conquer |
| HashMap/HashSet | O(n) | Frequency count |
| Sorted container | O(n) | TreeMap, Heap |

---

## 🔢 Back-of-Envelope Numbers

### Storage
| Size | Bytes | Example |
|------|-------|---------|
| 1 KB | 10³ | Short text |
| 1 MB | 10⁶ | Small image |
| 1 GB | 10⁹ | 1 hour video |
| 1 TB | 10¹² | Database |
| 1 PB | 10¹⁵ | Large data warehouse |

### Time
| Duration | Seconds | Use |
|----------|---------|-----|
| 1 hour | 3,600 | |
| 1 day | 86,400 | Daily QPS calculations |
| 1 month | 2.5 × 10⁶ | Monthly estimations |
| 1 year | 3.15 × 10⁷ | Yearly storage |

### Quick Conversions
- 1 million requests/day ≈ 12 requests/second
- 1 billion requests/day ≈ 12,000 requests/second
- 100 million users × 1 KB = 100 GB

---

## 📋 Complexity Comparison

```
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!)

For n = 1,000:
O(1)       = 1                    (constant)
O(log n)   = 10                   (log₂ 1000 ≈ 9.97)
O(n)       = 1,000                (one thousand)
O(n log n) = 10,000               (1000 × 10)
O(n²)      = 1,000,000            (one million)
O(2ⁿ)      = 10^301               (larger than atoms in universe)
O(n!)      = 10^2567              (incomprehensibly large)
```

---

## ✅ Interview Quick Check

Before stating complexity, verify:
- [ ] Did I account for all loops?
- [ ] Did I account for recursive calls?
- [ ] Did I consider the data structure operations used?
- [ ] Did I analyze space for any additional data structures?
- [ ] Can I explain WHY it's this complexity?

---

*Bookmark this page for quick reference! 📌*
