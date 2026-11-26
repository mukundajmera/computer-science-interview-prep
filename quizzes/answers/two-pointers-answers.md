# 🔁 Two Pointers Quiz - Answer Key

> Answer Distribution: A: 8, B: 8, C: 8, D: 8

## Section 1: Pattern Recognition (8 questions)

### Question 1
1. **C) Two pointers from ends**

**Explanation:**
For a sorted array, pointers starting at opposite ends can safely eliminate candidates. If `sum < target`, incrementing the left pointer is the *only* way to increase the sum. If `sum > target`, decrementing right decreases it.

**Complexity & Edge Cases:**
Time is O(N) using a single pass. Space is strictly O(1) because no auxiliary data structures are needed. Edge case: no pairs exist.

**Why others fail:**
Hash map (A) uses O(N) extra space. DFS (B) is overkill. Heap (D) is unnecessary and O(N) space.

### Question 2
2. **B) Monotonic pointer movement can eliminate ranges**

**Explanation:**
Two pointers work when moving a pointer strictly eliminates a subset of the search space that is guaranteed to be suboptimal or invalid. This monotonicity (e.g., sorted arrays or geometric container widths) guarantees correctness without backtracking.

**Complexity & Edge Cases:**
Time complexity is bounded by O(N) as pointers move monotonically. Space is O(1). Edge cases: arrays of size 0 or 1.

**Why others fail:**
Random insertions (A) disrupt pointer locations. Graph cycles (C) and exponential branching (D) require state tracking (DFS/BFS).

### Question 3
3. **C) Fast/slow (scan/write)**

**Explanation:**
For in-place compaction (like moving zeros to the end while maintaining order), a fast pointer scans the array to find valid elements, while a slow pointer tracks the next available write index. This guarantees stability and zero extra space.

**Complexity & Edge Cases:**
Time is O(N) for a single pass. Space is strictly O(1). Edge cases: array is already compacted, or array consists entirely of zeros.

**Why others fail:**
Opposite ends (B) destroys relative order (stability). Nested loops (D) degrade to O(N^2). Backtracking (A) is exponential.

### Question 4
4. **D) Sort Colors**

**Explanation:**
Sort Colors (Dutch National Flag) requires partitioning an array into 3 distinct regions (0s, 1s, 2s). It uses three pointers: `low` (boundary for 0s), `high` (boundary for 2s), and `current` (scanning the unknown region).

**Complexity & Edge Cases:**
Time is strictly O(N) in a single pass. Space is O(1). Edge cases: array is already sorted or contains only one color.

**Why others fail:**
3-sum (C) uses one anchor and two opposite pointers, not region boundaries. Binary search (A) and prefix sum (B) do not sort in place.

### Question 5
5. **B) Moving taller side cannot improve limiting height while width shrinks**

**Explanation:**
In Container With Most Water, the volume is limited by the shorter line. Moving the taller line inwards cannot possibly increase the height limit, but it *will* strictly decrease the width, guaranteeing a smaller volume. Therefore, we must move the shorter line to seek a taller boundary.

**Complexity & Edge Cases:**
Time is O(N). Space is O(1). This logical elimination safely discards N-1 combinations per step. Edge cases: identical heights on both ends.

**Why others fail:**
Taller side is not always wrong (D). Width increase is impossible (C) since pointers move inwards. It avoids duplicates (A).

### Question 6
6. **D) Avoid duplicate triplets**

**Explanation:**
In 3-Sum, the target is to find *unique* triplets. If the sorted array contains adjacent duplicates (e.g., `[-1, -1, 2]`), allowing the anchor loop to process the second `-1` will independently rediscover the exact same triplets, violating the uniqueness constraint.

**Complexity & Edge Cases:**
Skipping duplicates maintains O(N^2) time but aggressively prunes redundant branches, preventing the need for an O(N) space hash set to dedup results at the end.

**Why others fail:**
Cache locality (C) is unaffected. It is not just about memory (B), it is about correct unique output. Overflow (A) is unrelated.

### Question 7
7. **C) leftMax and rightMax**

**Explanation:**
Trapping Rain Water relies on the physical reality that water trapped above an index is bound by `min(leftMax, rightMax) - height[i]`. Two pointers allow tracking these global maxes dynamically from the outside in, avoiding O(N) prefix arrays.

**Complexity & Edge Cases:**
Time is O(N). Space is O(1). Edge cases: flat arrays, completely ascending/descending slopes trap 0 water.

**Why others fail:**
Prefix sums (A) use O(N) space. Parent pointers (D) are for union-find/trees. Global median (B) is statistically irrelevant here.

### Question 8
8. **C) Possible when invariant-driven elimination still holds**

**Explanation:**
While sorting is the most common enabler for two pointers, unsorted arrays can use the pattern if an elimination invariant still holds. For example, Trapping Rain Water and Container With Most Water run on unsorted arrays because geometric boundaries allow logical pruning.

**Complexity & Edge Cases:**
Time remains O(N). Space is O(1). Edge cases heavily depend on the specific physical or geometric logic driving the pointers.

**Why others fail:**
Impossible (D) and always requires sorting (B) ignore geometric problems. Recursion (A) is fundamentally different.

## Section 2: Invariants and Movement (10 questions)

### Question 9
9. **D) left++**

**Explanation:**
In a sorted array, the values strictly increase from left to right. If `nums[left] + nums[right] < target`, the only way to mathematically increase the sum is to move the left pointer to the right (`left++`), introducing a larger value.

**Complexity & Edge Cases:**
Time is O(N). Space is O(1). Edge cases: identical elements where we still just safely advance left.

**Why others fail:**
Decrementing right (B) makes the sum even smaller. Moving both (A) might skip the target. Restarting (C) breaks O(N).

### Question 10
10. **A) right--**

**Explanation:**
If the current sum is greater than the target in a sorted array, we must reduce the sum. The right pointer is at a large value; moving it left (`right--`) introduces a smaller value, safely eliminating the current overly-large combination.

**Complexity & Edge Cases:**
Time is O(N). Space is O(1). Edge case: pointers cross without finding a sum, safely returning null/empty.

**Why others fail:**
Incrementing left (D) increases the sum further. Swapping (B) does nothing. Binary search (C) is unnecessary overhead.

### Question 11
11. **A) do not increment `i` yet**

**Explanation:**
In Dutch National Flag, when `nums[i] == 2`, we swap it with `nums[right]` and decrement `right`. However, we *cannot* increment `i` yet because the value just swapped in from `right` is unknown (it could be a 0, 1, or 2) and must be evaluated on the next loop.

**Complexity & Edge Cases:**
Time is O(N). Space is O(1). Skipping this rule causes 0s to get stranded on the right side of the array.

**Why others fail:**
Incrementing `i` (B) skips evaluating the swapped element. Decrementing `i` (C) creates infinite loops. Resetting `left` (D) destroys the partition.

### Question 12
12. **B) prefix `[0, write)` contains non-zero values in original order**

**Explanation:**
In Move Zeroes, the `write` (slow) pointer strictly bounds the region of compacted, non-zero elements. After every step, the prefix array `[0, write)` is guaranteed to contain only non-zero values in their original relative order.

**Complexity & Edge Cases:**
Time is O(N). Space is O(1). Edge case: arrays with zero non-zero elements (write pointer never moves).

**Why others fail:**
Left side being sorted (A) is false; we preserve original order, not sorted order. Suffix sorted (C) is false. All zeros at end (D) is only true at final termination.

### Question 13
13. **A) `right - left`**

**Explanation:**
When finding valid triangles (`a + b > c`), if `nums[left] + nums[right] > nums[i]`, then keeping `right` fixed, *any* value between `left` and `right-1` combined with `nums[right]` will also be > `nums[i]` (because the array is sorted). This instantly counts `right - left` valid pairs.

**Complexity & Edge Cases:**
Time is O(N^2) for the outer loop + two pointers. Space is O(1). This combinatorial math trick prunes the inner loop.

**Why others fail:**
Adding 1 (C) misses the range. `i - right` (B) and `left + right` (D) are mathematically nonsensical for counting distances.

### Question 14
14. **C) move both and skip duplicates on both sides**

**Explanation:**
In 3-Sum, after recording a valid triplet `[anchor, left, right]`, we must move BOTH pointers to find entirely new combinations. Furthermore, we must use `while` loops to skip adjacent identical values on both sides to prevent recording duplicate triplets.

**Complexity & Edge Cases:**
Time remains O(N^2) as pointers never move backward. Space is O(1). Edge case: `[0, 0, 0, 0]` where skipping must handle bounds carefully.

**Why others fail:**
Moving one (B) guarantees a duplicate or invalid sum on the next step. Restarting (A) causes infinite loops. Resorting (D) is absurd.

### Question 15
15. **A) Right boundary is high enough for left limiter decision**

**Explanation:**
Water trapped at `left` depends on `min(leftMax, rightMax)`. If `height[left] <= height[right]`, then `leftMax <= rightMax` is guaranteed (as `leftMax` tracks `height[left]`). The bottleneck for `left` is firmly established by `leftMax`, making `rightMax` irrelevant for this specific column.

**Complexity & Edge Cases:**
Time is strictly O(N). Space is O(1). Edge cases: `height[left] == height[right]` handles identically and safely moves one side inward.

**Why others fail:**
Right side is not always max (C). Left side does not have global max (D). The array is explicitly unsorted (B).

### Question 16
16. **A) “I think it works on examples”**

**Explanation:**
In algorithmic interviews, "I think it works on examples" is a heuristic guess, not an invariant. A rigorous two-pointer solution must definitively prove why a pointer movement safely eliminates candidates without missing the optimal answer.

**Complexity & Edge Cases:**
Without a provable invariant, edge cases will inevitably fail, and complexity bounds cannot be mathematically justified.

**Why others fail:**
Partitions (D), termination progress (B), and provable suboptimality (C) are all extremely valid, rigorous invariants.

### Question 17
17. **C) Less memory, possible `O(n log n)` due to sorting**

**Explanation:**
Unsorted pair-sum normally uses a Hash Map (O(N) time, O(N) space). Converting it to Two-Pointers requires sorting the array first. Sorting drops the extra space to O(1) but increases the time complexity to O(N log N).

**Complexity & Edge Cases:**
This is the classic Space vs. Time trade-off in system design and coding. Edge case: if we need to return original indices, sorting requires an array of tuples, negating the O(1) space benefit.

**Why others fail:**
More memory/same time (B) is false. Less time (D) is false; N log N is slower than N. None (A) ignores computational reality.

### Question 18
18. **B) not skipping equal anchor values**

**Explanation:**
If the anchor loop `for i in range(n)` does not explicitly check `if i > 0 and nums[i] == nums[i-1]: continue`, the exact same target sum will be processed multiple times, flooding the output list with identical triplet arrays.

**Complexity & Edge Cases:**
Failing to skip anchors doesn't break O(N^2) time, but it violates the problem's strict uniqueness constraint. Deduping later requires an O(N) space HashSet.

**Why others fail:**
Multiplication (A) is unrelated. Not using append (D) is a syntax error, not a logic bug. Sorting descending (C) works fine if logic is reversed.

## Section 3: Complexity and Edge Cases (8 questions)

### Question 19
19. **B) `O(n)`**

**Explanation:**
The two pointers start at opposite ends. At every single step, either `left` increments or `right` decrements. Because they only move towards each other, they will cross after at most N steps. Thus, every element is evaluated at most once.

**Complexity & Edge Cases:**
Time complexity is strictly O(N). Space is O(1). Edge case: extremely large arrays process optimally without timeouts.

**Why others fail:**
O(1) (A) is impossible as we must read data. O(log n) (D) implies binary search. O(n^2) (C) implies nested loops.

### Question 20
20. **C) `O(1)`**

**Explanation:**
The Two-Sum-Sorted approach relies entirely on two integer variables (`left` and `right`) acting as indices. No hash maps, arrays, or recursive call stacks are instantiated.

**Complexity & Edge Cases:**
Extra space complexity is strictly O(1) constant space. This is the primary advantage over the O(N) space Hash Map approach for unsorted arrays.

**Why others fail:**
O(log n) (D), O(n) (B), and O(n^2) (A) falsely imply auxiliary data structures or deep recursion.

### Question 21
21. **C) `O(n^2)`**

**Explanation:**
After the O(N log N) sorting step, 3-Sum uses an outer loop that runs N times. Inside this loop, a Two-Pointer search runs in O(N) time. Multiplying the nested behaviors yields O(N * N).

**Complexity & Edge Cases:**
Time complexity is O(N^2), heavily dominating the initial O(N log N) sort. Space is O(1) (excluding the output array).

**Why others fail:**
O(n) (D) is impossible for combinations. O(n log n) (A) ignores the nested O(N) scan. O(n^3) (B) is the naive three-loop brute force.

### Question 22
22. **B) `O(n)` time, `O(1)` extra space**

**Explanation:**
Sort Colors (Dutch National Flag) explicitly tests the ability to partition data in a single pass. By using three pointers and swapping in-place, the algorithm inspects each element exactly once.

**Complexity & Edge Cases:**
Time is strictly O(N). Space is strictly O(1) because swaps are executed in-place. Edge case: all identical elements sort cleanly in one pass.

**Why others fail:**
O(n log n) (A) is standard comparison sort. O(n) space (C) implies creating a new array. O(n^2) (D) is bubble sort.

### Question 23
23. **B) `O(1)`**

**Explanation:**
The two-pointer optimization for Trapping Rain Water dynamically tracks the `leftMax` and `rightMax` using two variables while pointers move inward. This entirely replaces the need to pre-compute and store O(N) prefix and suffix maximum arrays.

**Complexity & Edge Cases:**
Space complexity drops from O(N) to strictly O(1). Time remains O(N). Edge case: massive terrains do not cause OutOfMemory errors.

**Why others fail:**
O(N) (C) is the naive DP approach. O(log n) (A) and O(n^2) (D) are completely unrelated bounds.

### Question 24
24. **D) empty array**

**Explanation:**
In Trapping Rain Water, the initialization immediately sets `right = len(height) - 1`. If the array is empty, this evaluates to `-1`. Accessing `height[-1]` or entering the loop logic with invalid pointers causes out-of-bounds exceptions.

**Complexity & Edge Cases:**
Guarding with `if not height: return 0` is an O(1) time/space check that safely neutralizes the edge case before pointer initialization.

**Why others fail:**
Negative indexes (B) are impossible for array lengths. Duplicates (A) are handled safely by standard logic. Prime values (C) are irrelevant.

### Question 25
25. **B) It ignores the requested in-place partitioning insight**

**Explanation:**
Counting sort requires two passes: one to count the 0s, 1s, and 2s, and a second pass to overwrite the array. The prompt's strict intent (and follow-up constraint) is to achieve the partition in a *single* pass using pointer swaps.

**Complexity & Edge Cases:**
While counting sort is technically O(N) time and O(1) space, it fails the "one-pass" constraint explicitly requested by interviewers testing the Dutch National Flag invariant.

**Why others fail:**
It is not wrong (C). It can sort integers easily (A). It does not use recursion (D).

### Question 26
26. **A) memory medium has write cost constraints**

**Explanation:**
When writing to memory (like Flash/SSD, or cache lines in concurrent systems) is significantly slower or more degrading than reading, algorithms must minimize the physical `write` operations. The optimal Move-Zeroes avoids writing to the array if no zeros have been encountered.

**Complexity & Edge Cases:**
An optimized pointer approach does `if current != 0 and slow != current: swap; slow++`. This saves O(N) writes when the array is mostly non-zeros. Space remains O(1).

**Why others fail:**
Multi-core CPUs (D), sorted arrays (C), and unique values (B) do not inherently penalize write operations over reads.

## Section 4: System Design Adjacency (6 questions)

### Question 27
27. **D) Cache eviction metadata cleanup**

**Explanation:**
In memory-constrained environments, caching systems (like Redis/Memcached) often run background compaction. Using a fast/slow pointer logic allows the system to overwrite expired/evicted cache metadata entries in-place without allocating massive new memory blocks.

**Complexity & Edge Cases:**
This achieves O(N) compaction time with O(1) extra memory overhead, critical for systems that are already memory-bound.

**Why others fail:**
DNS recursion (A), TLS (C), and API versioning (B) are networking and routing concepts, unrelated to memory array compaction.

### Question 28
28. **D) Constraint-driven search-space pruning**

**Explanation:**
Two-pointer elimination (e.g. moving a pointer because a side is definitively too small) maps perfectly to constraint-driven search-space pruning in system design. If a partition or shard mathematically cannot contain the answer, we drop it entirely without querying.

**Complexity & Edge Cases:**
This reduces systemic load from O(N) exhaustiveness to O(1) targeted queries. Edge case: ensuring the pruning logic is flawless to avoid dropping valid data.

**Why others fail:**
Brute force (B), randomized choice (A), and UI design (C) are antithetical to rigorous mathematical elimination.

### Question 29
29. **A) Sliding window with pointer contraction**

**Explanation:**
A rate limiter storing raw timestamps in a queue or array must clean up old data. Advancing a left pointer to skip over timestamps older than `now - window` is identically equivalent to variable sliding-window contraction.

**Complexity & Edge Cases:**
Time is amortized O(1) per request. Space is O(Requests in Window). The pointer physically releases memory references for Garbage Collection.

**Why others fail:**
Dijkstra (B), Union Find (C), and Quickselect (D) are unrelated algorithms.

### Question 30
30. **D) State invariants and discuss trade-offs out loud**

**Explanation:**
Strong interviewers look for engineers who can vocalize the "why". Explicitly stating the invariant (e.g., "left max is strictly smaller, so we can commit to this water volume") demonstrates deep architectural understanding, not just rote memorization of pointer updates.

**Complexity & Edge Cases:**
Discussing state invariants directly leads to accurate time/space complexity analysis and proves the ability to document complex system states.

**Why others fail:**
Silent coding (B) hides thought process. Skipping complexity (C) fails a core rubric. Focusing on syntax (A) ignores algorithmic design.

### Question 31
31. **A) bounded state and partial visibility**

**Explanation:**
In streaming systems, the "array" is infinite and data arrives out of order. Two-pointer logic usually requires full visibility of boundaries (like `right = len - 1`). Adapting it requires bounded buffers (windows) and accepting partial visibility.

**Complexity & Edge Cases:**
Space complexity shifts from O(1) pointers to O(Window Size) buffers. Time must handle late arrivals (watermarks).

**Why others fail:**
Pointers can exist conceptually (D). Sorting is never free (C). Complexity always matters (B) at scale.

### Question 32
32. **D) “Invariant, elimination rule, complexity, and edge behavior are all explicit.”**

**Explanation:**
A senior wrap-up statement definitively asserts correctness by summarizing the structural proofs: the invariant holds at each step, the elimination rule strictly prunes dead ends, the time/space complexity is mathematically bounded, and edge cases are handled.

**Complexity & Edge Cases:**
This checks every box on an interviewer's grading rubric.

**Why others fail:**
Samples pass by luck (A). Feelings are not proofs (C). Optimizing later (B) is a weak excuse if the optimal pattern is expected.
