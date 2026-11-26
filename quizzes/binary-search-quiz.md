# 🔎 Binary Search Quiz

> **32 questions to test your binary-search recognition, interval invariants, boundary discipline, answer-space reasoning, and system-design transfer**
>
> ⏱️ Time: 40 minutes | ⭐⭐⭐ Difficulty

---

## Section 1: Pattern Recognition (8 questions)

### Question 1 ⭐
Which signal most strongly suggests binary search?

**A)** Arbitrary graph reachability  
**B)** Need to enumerate every subset  
**C)** Ordered search space with a midpoint decision that discards one side  
**D)** Unordered lookup with exact key equality only  

---

### Question 2 ⭐
Lower-bound search is best described as finding:

**A)** any index where the target appears  
**B)** the first index where a predicate becomes true  
**C)** every valid subarray  
**D)** the largest value in an unsorted array  

---

### Question 3 ⭐⭐
Which problem is least likely to be solved by binary search?

**A)** minimum feasible shipping capacity  
**B)** first bad version  
**C)** all permutations of a string  
**D)** search insert position  

---

### Question 4 ⭐⭐
Binary search on answer is appropriate when:

**A)** every candidate must be returned  
**B)** recursion depth is the main bottleneck  
**C)** values are random and no predicate exists  
**D)** feasibility is monotonic across candidate answers  

---

### Question 5 ⭐⭐
In a rotated sorted array with distinct values, each midpoint usually reveals:

**A)** duplicate frequency  
**B)** at least one sorted half  
**C)** the exact pivot every time  
**D)** both halves are unsorted  

---

### Question 6 ⭐⭐
For a sorted array, `lower_bound(target)` returns:

**A)** the number of target occurrences  
**B)** any target index  
**C)** the last index whose value equals target  
**D)** the first index whose value is greater than or equal to target  

---

### Question 7 ⭐⭐⭐
Search in a row-major globally sorted matrix works by:

**A)** running DFS from the top-left cell  
**B)** using a heap of all cells  
**C)** mapping a virtual 1D midpoint to `(row, col)`  
**D)** sorting every row again  

---

### Question 8 ⭐⭐⭐
Which system-design scenario most directly maps to lower-bound reasoning?

**A)** normalizing a table into third normal form  
**B)** choosing a class name  
**C)** finding the first consistent-hash ring token at or after a key hash  
**D)** rendering a modal dialog  

---

## Section 2: Invariants and Boundary Mechanics (10 questions)

### Question 9 ⭐
For inclusive exact search over `[left, right]`, the usual loop guard is:

**A)** `left == right`  
**B)** `left < right` only  
**C)** `right < left`  
**D)** `left <= right`  

---

### Question 10 ⭐
Which midpoint formula avoids overflow in fixed-width integer languages?

**A)** `left + (right - left) // 2`  
**B)** `right - left * 2`  
**C)** `left // right`  
**D)** `(left + right) * 2`  

---

### Question 11 ⭐⭐
In a lower-bound search, if `nums[mid] >= target`, why set `right = mid`?

**A)** `mid` may be the first valid index  
**B)** the target must be absent  
**C)** all values to the left are invalid  
**D)** it makes the loop linear  

---

### Question 12 ⭐⭐
Why is `right = mid - 1` dangerous in a first-true search?

**A)** it always causes overflow  
**B)** it may discard the current first-true candidate  
**C)** it sorts the input  
**D)** it ignores values greater than target  

---

### Question 13 ⭐⭐
At the end of a half-open lower-bound loop, the return value is usually:

**A)** `left`  
**B)** `right - 1`  
**C)** `mid`  
**D)** `-1` without validation  

---

### Question 14 ⭐⭐
Which update can cause an infinite loop in a two-element range?

**A)** `right = mid` when `mid` may be the boundary  
**B)** `left = mid + 1` when left side is impossible  
**C)** `left = mid` without moving past `mid`  
**D)** returning immediately on equality  

---

### Question 15 ⭐⭐⭐
In search in rotated sorted array, `nums[left] <= nums[mid]` usually means:

**A)** the left half is sorted  
**B)** the array has duplicates  
**C)** the right half must contain the target  
**D)** the pivot is exactly `mid`  

---

### Question 16 ⭐⭐⭐
For finding the minimum in a rotated sorted array, if `nums[mid] > nums[right]`, the minimum is:

**A)** strictly to the right of `mid`  
**B)** always at `left`  
**C)** impossible to find in logarithmic time with distinct values  
**D)** at `mid` or to the left  

---

### Question 17 ⭐⭐⭐
In a minimum-feasible answer search, if `can(mid)` is true, what should usually happen?

**A)** restart the scan from zero  
**B)** discard `mid` with `left = mid + 1`  
**C)** keep `mid` and search left with `right = mid`  
**D)** return the maximum candidate  

---

### Question 18 ⭐⭐⭐
For a matrix with `cols` columns, a virtual index `mid` maps to column:

**A)** `mid // cols`  
**B)** `mid % cols`  
**C)** `mid + cols`  
**D)** `cols // mid`  

---

## Section 3: Complexity and Edge Cases (8 questions)

### Question 19 ⭐
Classic binary search target complexity is:

**A)** `O(n)` time, `O(1)` space  
**B)** `O(log n)` time, `O(1)` space  
**C)** `O(n^2)` time  
**D)** `O(n log n)` time  

---

### Question 20 ⭐⭐
Binary search on answer with an `O(n)` feasibility check usually costs:

**A)** `O(1)`  
**B)** `O(n^2)` always  
**C)** `O(n log range)`  
**D)** `O(log n)` total regardless of check cost  

---

### Question 21 ⭐⭐
Duplicates in rotated sorted array search can:

**A)** remove the need for boundary checks  
**B)** make the array globally sorted  
**C)** make the sorted-half signal ambiguous and degrade worst-case time  
**D)** always improve the time complexity  

---

### Question 22 ⭐
For exact search in an empty sorted array, the correct result is usually:

**A)** index `0`  
**B)** `-1` or false, depending on the prompt  
**C)** the midpoint  
**D)** target value  

---

### Question 23 ⭐⭐
If every value is less than target in search insert position, lower bound returns:

**A)** `n - 1`  
**B)** `n`  
**C)** `0`  
**D)** `-1`  

---

### Question 24 ⭐⭐
Why do many interviewers prefer `left + (right - left) // 2` over `(left + right) // 2`?

**A)** it handles unsorted arrays  
**B)** it changes `O(n)` to `O(log n)`  
**C)** it returns the rightmost duplicate  
**D)** it avoids integer overflow in fixed-width languages  

---

### Question 25 ⭐⭐⭐
Why does virtual 1D binary search fail for a matrix where each row is sorted but row ranges overlap?

**A)** the target may be negative  
**B)** row-major order is not globally sorted  
**C)** the matrix has too many cells  
**D)** modulo is unavailable  

---

### Question 26 ⭐⭐⭐
If no ordering or monotonic predicate exists, the safest binary-search decision is:

**A)** do not use binary search; choose another pattern  
**B)** always use recursion  
**C)** binary search random indices  
**D)** sort silently and ignore output contract  

---

## Section 4: System Design Adjacency (6 questions)

### Question 27 ⭐⭐
Database index seek is related to binary search because it:

**A)** enumerates every row  
**B)** requires recursion in application code  
**C)** stores unsorted logs only  
**D)** narrows an ordered key space to a candidate page or row range  

---

### Question 28 ⭐⭐
Consistent-hash ring lookup often needs:

**A)** random node selection without hashing  
**B)** dynamic programming over all services  
**C)** topological sorting  
**D)** lower bound for the first token at or after the key hash, with wraparound  

---

### Question 29 ⭐⭐⭐
In an SSTable-style sparse index, binary search commonly finds:

**A)** the block whose key range may contain the requested key  
**B)** every duplicate log line  
**C)** the shortest network path  
**D)** all possible cache invalidations  

---

### Question 30 ⭐⭐⭐
Capacity planning can use binary search when:

**A)** the metric is unrelated to load  
**B)** adding capacity has no predictable effect  
**C)** every capacity must be deployed to production  
**D)** a candidate capacity either passes or fails a monotonic load test  

---

### Question 31 ⭐⭐⭐
Keyset pagination often resembles lower bound because the server finds:

**A)** the first record after a stable cursor key  
**B)** a graph cycle  
**C)** every page before the cursor  
**D)** the first random row in a table  

---

### Question 32 ⭐⭐⭐
Why should answer-space binary search mention predicate cost in production?

**A)** predicates are always free  
**B)** it removes all edge cases  
**C)** it changes sorted arrays into heaps  
**D)** expensive feasibility checks can dominate total latency and resource usage  

---

