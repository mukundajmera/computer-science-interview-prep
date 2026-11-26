# Heap / Priority Queue Quiz

> 32 multiple-choice questions plus written drills to test heap recognition, top-k invariants, two-heap medians, k-way merge, cooldown scheduling, and system-design transfer.
>
> Time: 40 minutes | Difficulty: Intermediate

## Section 1: Pattern Recognition

### Question 1
What is the main reason to use a heap?

A) It exposes the current minimum or maximum while supporting updates efficiently
B) It always sorts all values faster than comparison sort
C) It removes the need for extra state
D) It guarantees constant-time arbitrary deletion

### Question 2
Which prompt most strongly suggests a size-k heap?

A) Return all permutations
B) Find the kth largest value in a stream
C) Detect a directed cycle
D) Compute edit distance

### Question 3
For top k frequent elements, what should happen before heap processing?

A) Reverse the input
B) Build a frequency map
C) Run DFS
D) Convert values to strings

### Question 4
For kth largest using a heap of size `k`, which heap direction is most natural?

A) Min-heap
B) Max-heap of all values only
C) Queue
D) Stack

### Question 5
Which problem most directly uses two heaps?

A) Find Median from Data Stream
B) Number of Islands
C) Partition Labels
D) Binary Search

### Question 6
Which problem stores one current head from each active sorted source?

A) Reorganize String
B) Merge K Sorted Lists
C) Task Scheduler
D) Kth Largest Element

### Question 7
Which prompt needs a heap plus cooldown queue?

A) Task Scheduler with cooldown
B) Activity Selection
C) Clone Graph
D) Best Time to Buy and Sell Stock

### Question 8
Which prompt should make you consider squared distance as a priority key?

A) K Closest Points
B) Word Ladder
C) Gas Station
D) Course Schedule

## Section 2: Invariants and State

### Question 9
In kth largest with a size-k min-heap, what does the root represent after scanning all values?

A) The kth largest value
B) The largest value
C) The smallest input value always
D) The median

### Question 10
In top k frequent elements, what does the heap root represent when the heap is full?

A) The number of distinct values
B) The most frequent candidate in the whole input
C) The first input value
D) The least frequent candidate among the kept top-k values

### Question 11
In Merge K Sorted Lists, why is one heap entry per active list enough?

A) Each list is already sorted, so only its head can be the next global value
B) Linked lists cannot contain duplicates
C) Heaps cannot store more than k values
D) Sorting is impossible

### Question 12
For streaming median, which invariant must hold?

A) Both heaps must have exactly the same size always
B) The lower heap stores only positive numbers
C) Lower half values are <= upper half values, and heap sizes differ by at most one
D) The upper heap stores all values

### Question 13
For Reorganize String, why hold back the previously used character?

A) To prevent immediate adjacent reuse
B) To sort the output lexicographically
C) To reduce memory to zero
D) To count vowels

### Question 14
In Task Scheduler, when can a cooling task return to the heap?

A) Immediately after it runs
B) When its next allowed time has arrived
C) Only after all tasks finish
D) Never

### Question 15
For K Closest Points with a max-heap of size `k`, what is the root?

A) The farthest point among the kept closest candidates
B) The closest point in the input
C) The median point
D) The first point scanned

### Question 16
Why is heap array order not the same as sorted order?

A) A heap only guarantees the root priority relationship, not full ordering across siblings
B) Heaps store no comparable values
C) Heap operations are random
D) Sorting is disabled after insertion

## Section 3: Complexity and Edge Cases

### Question 17
Kth largest with a size-k heap over `n` values costs:

A) `O(log n)` total time
B) `O(1)` time and `O(1)` space
C) `O(n^2)` time and `O(n^2)` space
D) `O(n log k)` time and `O(k)` space

### Question 18
Merge K Sorted Lists with `N` total nodes and `k` lists costs:

A) `O(k log N)` time
B) `O(N^2)` time always
C) `O(N log k)` time
D) `O(1)` time

### Question 19
What should top-k code clarify when counts tie?

A) Whether any tied answer is acceptable or deterministic order is required
B) Whether arrays are directed
C) Whether recursion is allowed
D) Whether heap memory is zero

### Question 20
For K Closest Points, why avoid square roots?

A) Square roots make the answer impossible
B) Squared distance preserves ordering and is cheaper
C) Heap comparisons cannot use numbers
D) Distance should be sorted lexicographically

### Question 21
What is the impossibility condition for Reorganize String?

A) Some character count exceeds `(n + 1) / 2`
B) The string length is even
C) The alphabet has more than two letters
D) The first and last characters match

### Question 22
For streaming median, `findMedian` after rebalancing is:

A) `O(n log n)`
B) `O(n^2)`
C) `O(1)`
D) impossible without sorting

### Question 23
What is a common max-heap implementation trick in min-heap-only languages?

A) Negate numeric priorities
B) Reverse the input permanently
C) Use recursion instead
D) Store only strings

### Question 24
What is a common top-k heap mistake?

A) Letting the heap grow to all `n` items when size `k` is enough
B) Counting frequencies
C) Handling duplicates
D) Naming the priority key

## Section 4: System Design Transfer

### Question 25
How does k-way merge map to system design?

A) Encrypting secrets
B) Rendering CSS
C) Running schema migrations
D) Merging sorted logs, feeds, or search shard results

### Question 26
How does top-k map to observability systems?

A) Heavy hitters such as top error codes or hottest endpoints
B) All-pairs shortest paths
C) Static page rendering
D) Deadlock detection only

### Question 27
What production risk appears in priority schedulers?

A) Markdown headings
B) File extension mismatch
C) Starvation of lower-priority work
D) Class naming

### Question 28
Which metric can validate a heap-based scheduler?

A) Queue age, deadline misses, and starvation rate
B) Number of images in a README
C) CSS selector count
D) Function name length

### Question 29
What should a distributed top-k design do after local shard top-k results?

A) Return only the first shard's candidates
B) Merge local candidates with a second-stage heap or reducer
C) Run DFS from every value
D) Sort source code files

### Question 30
Why might approximate heavy hitter algorithms replace exact heaps?

A) The stream is too large to store exact counts for every key
B) Heaps cannot compare counts
C) Top-k never needs accuracy
D) Approximation always gives exact answers

### Question 31
Which phrase is strongest in a heap interview wrap-up?

A) "A heap makes everything constant time."
B) "I do not need to define the entries."
C) "Heap order is sorted order."
D) "The heap stores the active frontier, and its size bound gives the `log k` factor."

### Question 32
What should you say when arbitrary priority updates are required?

A) Consider lazy deletion, an indexed heap, or a different ordered structure
B) Ignore stale entries forever
C) Sort once at the beginning
D) Use recursion only

## Written Drill Set

A. State the invariant for kth largest with a size-k min-heap.
B. Explain why k-way merge needs only one heap entry per active source.
C. Explain the two invariants in streaming median.
D. Show why Reorganize String is impossible when one count is too high.
E. Compare heap and quickselect for K Closest Points.
F. Describe how to validate a production priority scheduler.
