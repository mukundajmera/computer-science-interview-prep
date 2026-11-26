# 🔎 Binary Search Quiz - Answer Key

## Section 1: Pattern Recognition (8 questions)

### Question 1
1. **C) Ordered search space with a midpoint decision that discards one side**

**Explanation:**
Binary search fundamentally relies on halving the search space at each step. An ordered search space with a midpoint decision allows us to safely discard half the candidates, maintaining the invariant that the target (if present) must be in the remaining half.

**Complexity & Edge Cases:**
Time complexity is strictly O(log n) because the search space is halved at each step. Space complexity is O(1) for iterative implementations. Edge cases include empty arrays (handled by immediate return) and arrays with 1 element.

**Why others fail:**
Graph reachability (A) implies DFS/BFS. Enumerating subsets (B) is exponential backtracking. Unordered exact match (D) is a hash map (O(1)).

### Question 2
2. **B) the first index where a predicate becomes true**

**Explanation:**
The lower bound invariant seeks the boundary where a condition flips from false to true (or finding the first element >= target). The search space is continually narrowed until `left == right`, strictly preserving the index of the first true predicate.

**Complexity & Edge Cases:**
Time is O(log n). Space is O(1). Edge cases involve scenarios where all elements are false (returns n) or all elements are true (returns 0).

**Why others fail:**
Option A describes exact search. Option C implies returning a range. Option D is an unsorted max-finding problem (O(n)).

### Question 3
3. **C) all permutations of a string**

**Explanation:**
Generating permutations cannot benefit from search space halving because every single permutation must be visited and constructed. There is no monotonicity to exploit.

**Complexity & Edge Cases:**
Permutations take O(n! * n) time and O(n) space for the recursion stack. Binary search is inapplicable here.

**Why others fail:**
First bad version (A) and search insert position (B) are classic monotonic functions. Minimum capacity (D) is binary search on answer.

### Question 4
4. **D) feasibility is monotonic across candidate answers**

**Explanation:**
Binary search on answer requires a monotonic predicate: if answer X is feasible, all answers > X (or < X) must also be feasible. This allows us to halve the candidate range `[min_possible, max_possible]`.

**Complexity & Edge Cases:**
Time complexity is O(F * log(Range)), where F is the time to evaluate the feasibility predicate. Space is typically O(1). Edge cases: maximum answer exceeds integer limits, requiring careful mid calculation.

**Why others fail:**
Random values (B) prevent halving. Returning all candidates (C) is linear. Recursion depth (D) is a stack limit concern, not a driver for binary search.

### Question 5
5. **B) at least one sorted half**

**Explanation:**
In a rotated sorted array without duplicates, slicing it at any midpoint guarantees that at least one of the two halves (either `[left, mid]` or `[mid, right]`) is strictly sorted. This invariant dictates which side we can confidently search or discard.

**Complexity & Edge Cases:**
Time complexity is O(log n) since we discard half the array each time. Space is O(1). Edge cases include an un-rotated array and an array of size 1 or 2.

**Why others fail:**
Option A is mathematically impossible. Option C is false (pivot is often not the mid). Option D is explicitly contradicted by "distinct values".

### Question 6
6. **D) the first index whose value is greater than or equal to target**

**Explanation:**
The `lower_bound` function maintains the invariant of finding the first position where an element can be inserted without violating the sorted order. This corresponds exactly to the first element that is >= the target.

**Complexity & Edge Cases:**
Time complexity is O(log n) and space is O(1). An important edge case is when the target is greater than all elements, returning `n` (out of bounds).

**Why others fail:**
Option B describes an upper-bound-like or exact-match query. Option C is for standard binary search. Option D is a frequency count.

### Question 7
7. **C) mapping a virtual 1D midpoint to `(row, col)`**

**Explanation:**
A globally sorted matrix can be conceptualized as a single 1D sorted array. By mapping a 1D index `mid` back to 2D coordinates using `row = mid // cols` and `col = mid % cols`, we maintain the standard binary search invariant on the virtual 1D array.

**Complexity & Edge Cases:**
Time complexity is O(log(R * C)), where R and C are rows and columns. Space is O(1). Edge cases: empty matrix or empty rows.

**Why others fail:**
DFS (A) takes O(R*C). Sorting again (C) is redundant and O(N log N). Using a heap (D) is O(R*C log(R*C)) and ignores the pre-sorted nature.

### Question 8
8. **C) finding the first consistent-hash ring token at or after a key hash**

**Explanation:**
In a consistent hash ring, a key maps to the first node whose hash is greater than or equal to the key's hash. This is the exact definition of a lower-bound binary search on a sorted array of node tokens.

**Complexity & Edge Cases:**
Time complexity is O(log N) where N is the number of nodes (or virtual nodes). Wraparound logic (modulo N) handles the edge case where the key hash is greater than the largest token.

**Why others fail:**
Rendering a dialog (B) and choosing class names (C) are unrelated to algorithms. Normalizing a table (D) is a database schema design process.

## Section 2: Invariants and Boundary Mechanics (10 questions)

### Question 9
9. **D) `left <= right`**

**Explanation:**
For an inclusive range `[left, right]`, the search is only exhausted when the interval is empty, which happens when `left > right`. Therefore, `left <= right` guarantees we inspect the final element when `left == right`.

**Complexity & Edge Cases:**
Time complexity is O(log n). Space is O(1). Edge cases: skipping this equals check can lead to returning -1 when the target is at the exact `left == right` index.

**Why others fail:**
`left < right` (A) skips the final candidate. `left == right` (C) and `right < left` (D) immediately terminate the loop incorrectly.

### Question 10
10. **A) `left + (right - left) // 2`**

**Explanation:**
The formula `left + (right - left) // 2` mathematically equals `(left + right) // 2`, but avoids the intermediate step of adding two potentially large integers, thus preventing integer overflow in languages with fixed-width bounds.

**Complexity & Edge Cases:**
Time and space remain O(1) for the calculation. This gracefully handles the edge case where `left` and `right` are near INT_MAX.

**Why others fail:**
Option B and C are mathematically incorrect. Option D is integer division of the pointers, which is meaningless for finding a midpoint.

### Question 11
11. **A) `mid` may be the first valid index**

**Explanation:**
In a lower-bound search, we want the *first* true condition. If `nums[mid] >= target`, `mid` itself might be the correct answer. Setting `right = mid` retains this candidate while aggressively narrowing the search space to its left.

**Complexity & Edge Cases:**
Time complexity is O(log n). Space is O(1). This requires a `left < right` loop guard to prevent infinite loops when `left == right`.

**Why others fail:**
Option B is false (target might be present). Option C is the opposite of the truth (values to the left might be valid). Option D incorrectly asserts it changes time complexity.

### Question 12
12. **B) it may discard the current first-true candidate**

**Explanation:**
If the predicate is true at `mid` and we are looking for the *first* true instance, `mid` is a valid candidate. Setting `right = mid - 1` explicitly discards `mid` from the search space, potentially losing the correct answer forever.

**Complexity & Edge Cases:**
This breaks the algorithm's correctness, though time complexity remains O(log n). Edge cases include when `mid` is exactly the first true index.

**Why others fail:**
It does not cause overflow (A), it does not sort the input (C), and it is not about ignoring greater values (D).

### Question 13
13. **A) `left`**

**Explanation:**
In a half-open or `left < right` loop where `right = mid` and `left = mid + 1`, the pointers converge such that `left == right` at termination. Returning `left` (or `right`) gives the correct boundary index.

**Complexity & Edge Cases:**
Time complexity is O(log n). Space is O(1). The edge case is when the target is larger than all elements, returning `n` which must be handled safely.

**Why others fail:**
`mid` (A) is out of scope. `right - 1` (B) is incorrect because `right` itself is the boundary. Returning `-1` (D) fails to provide the insertion point.

### Question 14
14. **C) `left = mid` without moving past `mid`**

**Explanation:**
In a two-element range `[left, right]` where `mid = (left + right) // 2` (truncating down), `mid` equals `left`. If the update logic is `left = mid`, the state does not change, causing an infinite loop.

**Complexity & Edge Cases:**
This leads to an O(infinity) Time Limit Exceeded error. The edge case of `right == left + 1` is the exact trigger for this bug.

**Why others fail:**
Option B properly shrinks the window. Option C is safe because `mid < right` always holds. Option D simply terminates the loop successfully.

### Question 15
15. **A) the left half is sorted**

**Explanation:**
In a rotated sorted array, comparing the left boundary to the midpoint determines strictly sorted halves. If `nums[left] <= nums[mid]`, the left half `[left, mid]` is monotonically increasing without a pivot.

**Complexity & Edge Cases:**
O(log n) time, O(1) space. The edge case of duplicates (`nums[left] == nums[mid]`) makes this ambiguous and requires a different approach (e.g., `left += 1`).

**Why others fail:**
Option B is not guaranteed (target could be in the left half). Option C is false. Option D is not necessarily true (it could just be sorted).

### Question 16
16. **A) strictly to the right of `mid`**

**Explanation:**
If the midpoint value is strictly greater than the rightmost value, the array must rotate somewhere to the right of `mid`. Therefore, the minimum value cannot be `mid` or anything to its left; it is strictly to the right.

**Complexity & Edge Cases:**
O(log n) time. Space is O(1). Edge cases involve un-rotated arrays, where `nums[mid] < nums[right]` directs the search leftward.

**Why others fail:**
Option B is incorrect because `mid` is greater than `right`, so it can't be the minimum. Option C is false. Option D is false as it can be found in O(log n).

### Question 17
17. **C) keep `mid` and search left with `right = mid`**

**Explanation:**
For minimum-feasible search, if `mid` is feasible, we want to try and find a smaller feasible answer. We keep `mid` as a candidate (by setting `right = mid`) and continue searching the left half.

**Complexity & Edge Cases:**
Time is O(F * log(Range)). Space is O(1). Edge cases: if no candidates are feasible, the loop terminates without finding a valid answer.

**Why others fail:**
Option B discards the known valid answer. Option C returns the maximum, but we want the minimum. Option D breaks the O(log N) halving.

### Question 18
18. **B) `mid % cols`**

**Explanation:**
A 2D matrix mapped to a 1D array of length `rows * cols` uses division and modulo for coordinate translation. The column index cycles every `cols` elements, making `mid % cols` the exact mathematical mapping for the column.

**Complexity & Edge Cases:**
Mathematical O(1) translation ensures the binary search remains O(log(R*C)). Edge case: `cols = 0` causes division by zero, handled by initial matrix validation.

**Why others fail:**
`mid // cols` (A) gives the row, not the column. `cols // mid` (C) and `mid + cols` (D) are mathematically nonsensical for 2D mapping.

## Section 3: Complexity and Edge Cases (8 questions)

### Question 19
19. **B) `O(log n)` time, `O(1)` space**

**Explanation:**
Classic binary search strictly halves the active `[left, right]` window on each iteration. Since the range reduces by a factor of 2, it takes logarithmic steps to isolate the target or exhaust the array.

**Complexity & Edge Cases:**
Time complexity is strictly O(log n). Space is O(1) as it only requires two pointers. Edge case: arrays of size 0 or 1.

**Why others fail:**
O(n) time (B) is a linear scan. O(n log n) (C) implies sorting. O(n^2) (D) is nested loops.

### Question 20
20. **C) `O(n log range)`**

**Explanation:**
The outer binary search loop runs `O(log(Range))` times. Inside this loop, we execute a feasibility check that takes `O(n)` time. These multiply together because the check runs every iteration.

**Complexity & Edge Cases:**
Total time is O(n * log(Range)). Space is often O(1). Edge cases: large ranges might cause integer overflow, and F(n) might have its own edge cases (e.g., n=0).

**Why others fail:**
O(log n) (A) ignores the cost of the check. O(n^2) (C) is a brute-force combination. O(1) (D) is impossible.

### Question 21
21. **C) make the sorted-half signal ambiguous and degrade worst-case time**

**Explanation:**
If duplicates exist (e.g., `[3, 1, 3, 3, 3]`), comparing `nums[left] == nums[mid]` provides no information about which half is sorted. The invariant is broken, forcing a linear fallback `left += 1` to restore predictability.

**Complexity & Edge Cases:**
Worst-case time degrades to O(n) when the array is mostly identical elements. Space remains O(1). Edge case: all elements are the same.

**Why others fail:**
It worsens, not improves (B) the time complexity. It does not remove boundary checks (C) or make it globally sorted (D).

### Question 22
22. **B) `-1` or false, depending on the prompt**

**Explanation:**
An empty array `[]` has `left = 0` and `right = -1`. The loop condition `left <= right` immediately evaluates to false, terminating the search without accessing any out-of-bounds indices.

**Complexity & Edge Cases:**
Time complexity is O(1) for this edge case. Space is O(1). Safely returning -1 (or false) respects the contract of an exact search.

**Why others fail:**
Index 0 (B) would be an out-of-bounds error. The midpoint (C) cannot be calculated. The target value (D) is not an index.

### Question 23
23. **B) `n`**

**Explanation:**
Lower bound looks for the first element >= target. If all elements are strictly less than the target, the condition is never met. The `left` pointer increments until it exceeds the array bounds, stopping at index `n`.

**Complexity & Edge Cases:**
Time complexity is O(log n). Space is O(1). Returning `n` correctly signals that the target should be appended to the end of the array to maintain sort order.

**Why others fail:**
0 (A) implies it is smaller than all elements. `n-1` (B) points to a smaller element. `-1` (D) loses the insertion position information.

### Question 24
24. **D) it avoids integer overflow in fixed-width languages**

**Explanation:**
The calculation `left + right` can exceed the maximum representable integer (e.g., 2^31 - 1 in Java/C++). Using `left + (right - left) // 2` maintains the exact same mathematical midpoint while keeping intermediate values strictly smaller than the maximum bounds.

**Complexity & Edge Cases:**
Time and space complexity are completely unaffected (O(1) math). This directly prevents integer overflow crashes on massive arrays.

**Why others fail:**
It does not alter time complexity (A). It does not handle unsorted arrays (C) or affect duplicate handling (D).

### Question 25
25. **B) row-major order is not globally sorted**

**Explanation:**
Virtual 1D binary search requires a strict global ordering. If rows overlap (e.g., row 1 ends with 10, row 2 starts with 5), mapping `mid` to a 2D coordinate breaks monotonicity; a larger 1D index might point to a smaller value.

**Complexity & Edge Cases:**
This breaks the logarithmic halving invariant entirely. The fallback is often searching row by row (O(R log C)) or starting from the top-right corner (O(R + C)).

**Why others fail:**
Too many cells (A) is a resource issue, not logical. Negative targets (B) don't break sorting. Modulo (D) is a basic operator.

### Question 26
26. **A) do not use binary search; choose another pattern**

**Explanation:**
Binary search is fundamentally predicated on eliminating halves of the search space based on a monotonic condition or sorting. Without it, you cannot guarantee you aren't discarding the target.

**Complexity & Edge Cases:**
Binary search is invalid here. You must use O(n) linear scan, hash maps, or another algorithm. Edge case: random unsorted arrays.

**Why others fail:**
Sorting silently (B) mutates the input, breaking index-based questions. Searching random indices (C) is O(n) average but O(infinity) worst case. Recursion (D) is just a mechanism.

## Section 4: System Design Adjacency (6 questions)

### Question 27
27. **D) narrows an ordered key space to a candidate page or row range**

**Explanation:**
B-Trees and database indexes are hierarchical sorted structures. At each node, the database uses binary-search-like logic to narrow down the ordered key space to determine which child page contains the target range.

**Complexity & Edge Cases:**
Time complexity is O(log N) disk reads. Space is proportional to tree depth. Edge case: heavily fragmented indexes might degrade performance.

**Why others fail:**
Enumerating rows (B) is a full table scan. Unsorted logs (C) require linear scan. Recursion (D) is not strictly required.

### Question 28
28. **D) lower bound for the first token at or after the key hash, with wraparound**

**Explanation:**
In consistent hashing, nodes are sorted by their token hash on a ring. To find the correct node for a data key, the system uses a lower-bound search to find the first node token >= the key hash. Wraparound handles keys larger than all tokens.

**Complexity & Edge Cases:**
Time complexity is O(log N) for the search. Space is O(N) to store the ring. Edge cases: adding/removing nodes requires maintaining the sorted array or tree.

**Why others fail:**
DP (B) is unrelated. Random nodes (C) breaks consistency. Topological sorting (D) is for dependency graphs.

### Question 29
29. **A) the block whose key range may contain the requested key**

**Explanation:**
SSTables (like in Cassandra/RocksDB) maintain sorted keys but don't keep every key in memory. A sparse index keeps a subset of keys (e.g., block starts). Binary search on this sparse index quickly finds the specific disk block that *might* contain the key.

**Complexity & Edge Cases:**
Time complexity is O(log(Number of Blocks)) in memory + O(Block Size) on disk. Edge cases include keys missing from the block entirely.

**Why others fail:**
Finding every duplicate (B) is linear. Shortest path (C) is Dijkstra. Cache invalidations (D) are system states.

### Question 30
30. **D) a candidate capacity either passes or fails a monotonic load test**

**Explanation:**
When load testing, capacity often exhibits monotonic behavior: below threshold X, latency is fine; above X, it fails. We can binary search the capacity (e.g., number of pods) to find the minimum feasible capacity that satisfies SLAs.

**Complexity & Edge Cases:**
Time complexity is O(Cost of Load Test * log(Max Capacity)). Edge cases: non-monotonic behavior (e.g., adding pods causes database thrashing) invalidates the binary search.

**Why others fail:**
Unpredictable effects (A) break monotonicity. Deploying every capacity (C) is a linear scan. Unrelated metrics (D) provide no signal.

### Question 31
31. **A) the first record after a stable cursor key**

**Explanation:**
Keyset pagination (e.g., `WHERE id > last_seen_id ORDER BY id LIMIT 10`) relies on ordered database indexes. The engine essentially performs a lower-bound search to jump directly to `last_seen_id` before scanning the next 10 rows.

**Complexity & Edge Cases:**
Time complexity is O(log N) to find the start, plus O(K) to fetch rows. Space is O(1). Edge case: `last_seen_id` was deleted.

**Why others fail:**
Random rows (B) break pagination. Every page before (C) is offset pagination. Graph cycles (D) are unrelated.

### Question 32
32. **D) expensive feasibility checks can dominate total latency and resource usage**

**Explanation:**
In system design, the `O(n)` feasibility check in answer-space binary search might represent a heavy database query, network call, or simulation. Even if the search takes `log(Range)` steps, multiplying it by a high predicate cost causes massive latency.

**Complexity & Edge Cases:**
Production complexity highlights that O(N * log M) can easily exceed timeouts if N is a slow I/O bound check. Edge case: predicates that time out.

**Why others fail:**
Predicates are rarely free (A). It does not use heaps (C). It introduces edge cases related to latency and timeouts (D).
