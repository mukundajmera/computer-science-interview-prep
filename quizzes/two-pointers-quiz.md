# 🔁 Two Pointers Quiz

> **32 questions to test your two-pointer fundamentals, invariants, and interview adaptations**
>
> ⏱️ Time: 40 minutes | ⭐⭐⭐ Difficulty

---

## Section 1: Pattern Recognition (8 questions)

### Question 1 ⭐
You have a sorted array and need one pair that sums to target with minimal extra memory.

**A)** Hash map  
**B)** DFS  
**C)** Two pointers from ends  
**D)** Heap  

---

### Question 2 ⭐
Which condition most strongly suggests two pointers is viable?

**A)** Frequent random insertions  
**B)** Monotonic pointer movement can eliminate ranges  
**C)** Exponential branching  
**D)** Graph cycles  

---

### Question 3 ⭐
For stable in-place compaction (for example, move zeroes), which pointer model is typical?

**A)** Backtracking  
**B)** Opposite ends  
**C)** Fast/slow (scan/write)  
**D)** Triple nested loops  

---

### Question 4 ⭐⭐
Which problem naturally uses three pointers with region invariants?

**A)** Binary search  
**B)** Prefix sum  
**C)** 3-sum  
**D)** Sort Colors  

---

### Question 5 ⭐⭐
In container-with-water, why move the shorter boundary?

**A)** It avoids duplicates  
**B)** Moving taller side cannot improve limiting height while width shrinks  
**C)** Width increase compensates  
**D)** Taller side is always wrong  

---

### Question 6 ⭐⭐
In 3-sum after sorting, what is the major reason to skip duplicate anchors?

**A)** Prevent overflow  
**B)** Reduce memory only  
**C)** Improve cache locality  
**D)** Avoid duplicate triplets  

---

### Question 7 ⭐⭐
Trapping-rain-water two-pointer approach depends on which maintained state?

**A)** Prefix sums  
**B)** Global median  
**C)** leftMax and rightMax  
**D)** Parent pointers  

---

### Question 8 ⭐⭐⭐
Which statement is true about two pointers on unsorted arrays?

**A)** Requires recursion  
**B)** Always requires sorting first  
**C)** Possible when invariant-driven elimination still holds  
**D)** Impossible  

---

## Section 2: Invariants and Movement (10 questions)

### Question 9 ⭐
In two-sum-sorted, if current sum is less than target, next move is:

**A)** both move  
**B)** right--  
**C)** restart  
**D)** left++  

---

### Question 10 ⭐
In two-sum-sorted, if current sum is greater than target:

**A)** right--  
**B)** swap pointers  
**C)** binary search  
**D)** left++  

---

### Question 11 ⭐⭐
In Dutch National Flag sorting, after swapping `nums[i]` with `nums[right]` when value is `2`, what is correct?

**A)** do not increment `i` yet  
**B)** increment `i`  
**C)** decrement `i`  
**D)** reset `left`  

---

### Question 12 ⭐⭐
Move-zeroes stable invariant after each step should guarantee:

**A)** left side contains sorted values  
**B)** prefix `[0, write)` contains non-zero values in original order  
**C)** suffix is sorted  
**D)** all zeros already at end always  

---

### Question 13 ⭐⭐
In triangle counting, when `nums[left] + nums[right] > nums[i]`, how many triplets are added?

**A)** `right - left`  
**B)** `i - right`  
**C)** 1  
**D)** `left + right`  

---

### Question 14 ⭐⭐
3-sum pointer update after finding one valid triplet should:

**A)** restart at i=0  
**B)** move only one pointer  
**C)** move both and skip duplicates on both sides  
**D)** sort again  

---

### Question 15 ⭐⭐⭐
In trapping rain water, when `height[left] <= height[right]`, why can left side be finalized?

**A)** Right boundary is high enough for left limiter decision  
**B)** Because array is sorted  
**C)** Right side is always max  
**D)** Left side now has global max  

---

### Question 16 ⭐⭐⭐
Which is NOT a valid invariant style for pointer interviews?

**A)** “I think it works on examples”  
**B)** “Pointer always moves closer to termination”  
**C)** “All eliminated candidates are provably suboptimal”  
**D)** Region-by-region semantic partitions  

---

### Question 17 ⭐⭐⭐
When converting unsorted pair-sum to two pointers, what trade-off is introduced?

**A)** None  
**B)** More memory, same time  
**C)** Less memory, possible `O(n log n)` due to sorting  
**D)** Less time, more memory  

---

### Question 18 ⭐⭐⭐
Which bug most often breaks deduped 3-sum output?

**A)** integer multiplication  
**B)** not skipping equal anchor values  
**C)** sorting descending  
**D)** not using list append  

---

## Section 3: Complexity and Edge Cases (8 questions)

### Question 19 ⭐
Two-sum-sorted time complexity:

**A)** `O(1)`  
**B)** `O(n)`  
**C)** `O(n^2)`  
**D)** `O(log n)`  

---

### Question 20 ⭐
Two-sum-sorted extra space complexity:

**A)** `O(n^2)`  
**B)** `O(n)`  
**C)** `O(1)`  
**D)** `O(log n)`  

---

### Question 21 ⭐⭐
3-sum complexity after sorting:

**A)** `O(n log n)`  
**B)** `O(n^3)`  
**C)** `O(n^2)`  
**D)** `O(n)`  

---

### Question 22 ⭐⭐
Sort Colors canonical complexity target is:

**A)** `O(n log n)` time, `O(1)` extra space  
**B)** `O(n)` time, `O(1)` extra space  
**C)** `O(n)` time, `O(n)` space  
**D)** `O(n^2)` time  

---

### Question 23 ⭐⭐
Trapping Rain Water two-pointer solution uses extra space:

**A)** `O(log n)`  
**B)** `O(1)`  
**C)** `O(n)`  
**D)** `O(n^2)`  

---

### Question 24 ⭐⭐
Which edge case should be explicitly guarded in trapping rain water?

**A)** duplicate heights only  
**B)** negative indexes only  
**C)** all values prime  
**D)** empty array  

---

### Question 25 ⭐⭐⭐
Why is counting sort usually accepted for sort-colors but less preferred in interviews for this prompt?

**A)** It cannot sort integers  
**B)** It ignores the requested in-place partitioning insight  
**C)** It is always wrong  
**D)** It uses recursion  

---

### Question 26 ⭐⭐⭐
For move-zeroes, minimizing writes (instead of minimizing comparisons) is most relevant when:

**A)** memory medium has write cost constraints  
**B)** values are unique  
**C)** array is sorted  
**D)** CPU has multiple cores  

---

## Section 4: System Design Adjacency (6 questions)

### Question 27 ⭐⭐
Which system-design component often uses fast/slow compaction-like logic?

**A)** DNS recursion  
**B)** API versioning  
**C)** TLS handshake  
**D)** Cache eviction metadata cleanup  

---

### Question 28 ⭐⭐
Two-pointer elimination thinking is most similar to which SD mindset?

**A)** Randomized architecture choice  
**B)** Exhaustive brute force design  
**C)** UI-first iteration  
**D)** Constraint-driven search-space pruning  

---

### Question 29 ⭐⭐
A rate-limiter log cleanup pass that advances a left boundary over expired timestamps resembles:

**A)** Sliding window with pointer contraction  
**B)** Dijkstra  
**C)** Union find  
**D)** Quickselect  

---

### Question 30 ⭐⭐⭐
Which interview behavior gets higher score for coding+SD hybrid rounds?

**A)** Focus only on syntax  
**B)** Silent coding only  
**C)** Skip complexity discussion  
**D)** State invariants and discuss trade-offs out loud  

---

### Question 31 ⭐⭐⭐
When adapting two-pointer logic to streaming systems, the primary challenge is:

**A)** bounded state and partial visibility  
**B)** complexity no longer matters  
**C)** sorting always free  
**D)** pointers cannot exist  

---

### Question 32 ⭐⭐⭐
Best wrap-up statement for a strong two-pointer answer:

**A)** “It passed my sample case.”  
**B)** “I can optimize later.”  
**C)** “I used two pointers because it felt right.”  
**D)** “Invariant, elimination rule, complexity, and edge behavior are all explicit.”  

---

