# 🪟 Sliding Window Quiz - Answer Key

> Answer Distribution: A: 8, B: 8, C: 8, D: 8

## Section 1: Pattern Recognition (8 questions)

1. **C** Contiguous substring with a maintained validity condition

**Explanation:**
The sliding window pattern specifically tracks a contiguous subset (substring or subarray) while dynamically expanding (right pointer) and contracting (left pointer) to maintain a specific validity condition (like sum <= K or unique chars).

**Complexity & Edge Cases:**
Time is generally O(N) because each element is added and removed at most once. Space varies from O(1) to O(Alphabet). Edge cases: empty inputs or target criteria larger than the array.

**Why others fail:**
Non-contiguous choices (A) are dynamic programming. Graph reachability (B) is BFS/DFS. Arbitrary pairs (D) is two-pointers or sorting.

2. **B** exactly `k` consecutive elements

**Explanation:**
A fixed-size window enforces an invariant where `right - left + 1 == k`. We expand until the window hits size `k`, and then slide both pointers simultaneously (or slide right and pop left) to evaluate all contiguous subarrays of exactly length `k`.

**Complexity & Edge Cases:**
Time is strictly O(N) as we slide exactly N-k times. Space depends on state maintenance (e.g., O(1) for sums). Edge case: `k > N`, which usually returns 0 or null.

**Why others fail:**
Any `k` elements (A) implies combinations. Shortest path (D) is graph logic. Sorting (C) breaks contiguous order.

3. **C** whether the current window is valid or must shrink

**Explanation:**
For variable-size windows, the right pointer adds elements unconditionally. The "key predicate" evaluates this new state. If the window becomes invalid (e.g., sum > target), the left pointer must advance in a `while` loop to shrink the window until the predicate becomes valid again.

**Complexity & Edge Cases:**
Time is O(N) because the left pointer only moves forward. Space depends on the problem. Edge cases include windows that shrink to size 0.

**Why others fail:**
Graph nodes (B) are unrelated. Sorting items (D) is not window state. Recursion stopping (A) is a base case.

4. **D** negative numbers are allowed

**Explanation:**
The standard variable window relies on monotonicity: adding positive numbers strictly increases the sum, and removing them strictly decreases it. Negative numbers break this; adding a negative decreases the sum, so shrinking from the left no longer guarantees a predictable progression.

**Complexity & Edge Cases:**
When negatives exist, the O(N) sliding window fails, requiring a prefix-sum with a hash map or monotonic deque (O(N) to O(N log N)). Edge cases involve arrays of entirely negative numbers.

**Why others fail:**
All positive values (C) perfectly fit the template. `k=1` (A) is a trivial fixed window. Contiguous input (B) is required for sliding window.

5. **B** subarrays with exactly K distinct values

**Explanation:**
Counting substrings with *exactly* K constraints is difficult because the window state can be ambiguous. Converting the logic to `countAtMost(K) - countAtMost(K - 1)` relies on the monotonic property that a window valid for K-1 is strictly a subset of windows valid for K.

**Complexity & Edge Cases:**
Time is O(N) as it runs the standard sliding window twice. Space is bounded by the alphabet size. Edge case: K=0, which returns 0.

**Why others fail:**
Maximum of every window (D) is a deque problem. Binary search (C) and topological sort (A) are entirely different algorithmic families.

6. **D** fixed-size frequency-window matching

**Explanation:**
Permutation-in-string checks if any contiguous block in `s2` has the exact character frequencies of `s1`. This dictates a strictly fixed-size sliding window of length `len(s1)` moving over `s2` while comparing frequency maps.

**Complexity & Edge Cases:**
Time is O(N) to scan `s2`. Space is O(Alphabet), usually O(26) = O(1) for lowercase English. Edge case: `len(s1) > len(s2)` immediately returns false.

**Why others fail:**
Dynamic programming (C), graph coloring (B), and heaps (A) do not exploit the contiguous frequency matching invariant.

7. **C** monotonic deque of candidate indices

**Explanation:**
To maintain the maximum in a sliding window in linear time, we must discard elements that are mathematically obsolete. A monotonic decreasing deque stores indices, dropping elements from the back if they are smaller than the incoming element, and popping from the front when indices fall out of the window.

**Complexity & Edge Cases:**
Time is strictly O(N) because every index is pushed and popped at most once. Space is O(k) for the deque. Edge case: `k=1` where max is just the element itself.

**Why others fail:**
A stack (A) cannot remove expired elements from the bottom. Rebuilding a sorted array (D) degrades to O(N*k). Union-find (B) is for disjoint sets.

8. **C** API rate limiter over the last 60 seconds

**Explanation:**
A sliding window rate limiter counts requests within a moving contiguous time block (e.g., `[now - 60s, now]`). It maintains a valid state by shrinking (expiring old logs) and expanding (adding new requests), exactly mirroring the algorithmic pattern.

**Complexity & Edge Cases:**
Time is amortized O(1) per request if optimized with buckets. Space depends on traffic (O(Requests) for exact logs, O(Buckets) for arrays). Edge case: sudden massive bursts of traffic.

**Why others fail:**
Class factories (D) are OOP patterns. Normalization (B) is DB schema design. Leader election (A) is consensus.

## Section 2: Invariants and State (10 questions)

9. **D** remove the outgoing left item

**Explanation:**
In a fixed window of size `k`, maintaining the aggregate state (like a sum) requires adding the incoming `right` value and subtracting the outgoing `left` value (`right - k`). This avoids O(k) recalculations at every step.

**Complexity & Edge Cases:**
Time complexity remains O(1) per step, yielding O(N) total. Space is O(1). Edge case: handling the initial window setup before sliding begins.

**Why others fail:**
Sorting (B) destroys the array. Resetting the sum (A) forces an O(k) recalculation. Moving right backward (C) creates infinite loops.

10. **A** `right - left + 1`

**Explanation:**
Because the pointers `left` and `right` refer to 0-based array indices, an inclusive window covering both elements has a mathematical length of `right - left + 1`.

**Complexity & Edge Cases:**
This is an O(1) math operation crucial for correctly counting valid subarray lengths or updating max/min length variables. Edge case: `left > right` (length <= 0) must be handled.

**Why others fail:**
`right - left` (D) represents a half-open interval. `left - right + 1` (B) and `right + left` (C) yield incorrect math.

11. **A** every character count is at most one

**Explanation:**
A substring has no repeating characters if and only if the frequency count of every character currently inside the window is <= 1. The left pointer shrinks the window until the count of the newly added duplicate character drops back to 1.

**Complexity & Edge Cases:**
Time is O(N). Space is bounded by the character set (O(1) for ASCII). Edge case: empty string returns 0.

**Why others fail:**
Sorting (B) ruins substring order. Requiring lowercase (C) is a constraint, not the invariant. `left == right` (D) means size 1, which is valid but not the ONLY valid state.

12. **B** to keep distinct-count logic accurate

**Explanation:**
When solving "At Most K Distinct Characters", the map size dictates the number of distinct elements. If a character count drops to zero but the key remains in the map, `map.size()` will incorrectly report it as a distinct active character.

**Complexity & Edge Cases:**
Time remains O(N). Space is O(Distinct). Failing to remove the key breaks the core validity check of the algorithm.

**Why others fail:**
It does not change time complexity to constant (A). Hash maps are unordered, so sorting (C) is irrelevant. It has nothing to do with recursion (D).

13. **A** after the shrink loop restores validity

**Explanation:**
We are looking for the *longest valid* window. If the incoming right element makes the window invalid, the `while` loop shrinks it. We can only confidently record `best = max(best, length)` *after* the shrink loop guarantees the window is valid again.

**Complexity & Edge Cases:**
Time is O(N), Space is O(Alphabet). Edge cases: the entire string is valid, meaning the shrink loop never runs, but `best` must still be updated.

**Why others fail:**
Updating while invalid (C) records broken states. Updating before adding (B) misses the current element. Sorting keys (D) is unnecessary.

14. **C** inside the loop while `window_sum >= target`, before removing left

**Explanation:**
We want the *minimum* window that satisfies `sum >= target`. While the sum is valid, we record the length `min_len = min(min_len, length)` and *then* shrink the left pointer to see if an even smaller valid window exists.

**Complexity & Edge Cases:**
Time is O(N), Space is O(1). Edge case: if no window ever hits the target, `min_len` remains infinity and should return 0.

**Why others fail:**
Before reaching target (B) records invalid states. Waiting until the end (A) misses intermediate minimums. Binary search (D) is O(N log N) and sub-optimal.

15. **A** every start from `left` to `right` forms a valid subarray ending at `right`

**Explanation:**
When a window `[left, right]` is valid, every subarray ending at `right` and starting anywhere from `left` to `right` is also valid. The number of such subarrays is exactly the length of the window: `right - left + 1`.

**Complexity & Edge Cases:**
Time is O(N), Space is O(K). This mathematical trick avoids counting combinations recursively. Edge case: empty windows add 0.

**Why others fail:**
It is not the number of distinct values (B). It is not always K (C). It counts multiple subarrays, not just one window (D).

16. **A** indices let you expire entries that leave the window

**Explanation:**
A deque must expire elements that physically fall behind the `left` pointer. Storing indices allows us to easily check `if deque.front() < left_boundary` and pop it. Storing raw values provides no way to know *when* that value leaves the window.

**Complexity & Edge Cases:**
Time is O(N) and Space O(K). Resolving values is easy via `nums[deque.front()]`. Edge case: duplicate values are distinct indices, preserving stability.

**Why others fail:**
Indices are not always smaller (D). Values can be compared (B). Values do not require recursion (C).

17. **C** decreasing

**Explanation:**
To ensure the maximum is always instantly available at the front (O(1)), the deque maintains elements in strictly decreasing order. Any incoming larger element pops smaller elements from the back, as they can never be the maximum again.

**Complexity & Edge Cases:**
Amortized O(1) per element, O(N) total. Edge case: monotonically increasing arrays cause the deque to pop at every step.

**Why others fail:**
Increasing order (B) tracks minimums. Random (D) or original order (A) requires O(K) scans to find the max.

18. **B** each item enters and leaves the window at most once

**Explanation:**
Despite the nested `while` loop, both `left` and `right` pointers only ever move forward. Every element is processed (added to window) exactly once by `right`, and evicted (removed) at most once by `left`. 2N operations = O(N) time.

**Complexity & Edge Cases:**
Amortized O(1) per element guarantees strict linear time. Edge case: the inner loop might run N times in a single step, but then 0 times for the rest of the array.

**Why others fail:**
Nested loops are not always linear (A). Boundaries do not move backward (D). Hash maps (C) have overhead, though O(1).

## Section 3: Complexity and Edge Cases (8 questions)

19. **B** `O(n)` time, `O(1)` space

**Explanation:**
A fixed-size window of size K maintains a running sum by adding `right` and subtracting `left` (when window size > K). It touches every element once without nested scans.

**Complexity & Edge Cases:**
Time is strictly O(N). Space is O(1) as we only need variables for current_sum and max_sum. Edge cases: N < K returns an error or 0.

**Why others fail:**
O(nk) (A) indicates recalculating the sum from scratch. O(log n) (D) is binary search. O(n^2) (C) is brute force.

20. **C** `O(alphabet)` or `O(distinct active chars)`

**Explanation:**
The window tracks character frequencies or existence. The maximum number of distinct characters in the window cannot exceed the size of the alphabet (e.g., 26 for lowercase, 256 for ASCII).

**Complexity & Edge Cases:**
Space complexity is bounded by O(Alphabet) or O(min(N, Alphabet)), which resolves to O(1) for fixed alphabets. Time is O(N).

**Why others fail:**
O(1) regardless of alphabet (D) is false; large unicode sets require more space. O(n^2) (B) and O(log n) (A) are incorrect for space.

21. **C** 0

**Explanation:**
If the constraint allows *at most* 0 distinct characters, no characters are permitted. The only valid substring is the empty string.

**Complexity & Edge Cases:**
Time is O(1) by immediate return, or O(N) if it runs through the logic. Space is O(1). Returning 0 correctly fulfills the requirement.

**Why others fail:**
1 (D) contains 1 distinct char. Full string (A) violates K=0. Undefined (B) ignores the logical boundary.

22. **B** `len(s1) > len(s2)`

**Explanation:**
If the window we are looking for (`s1`) is longer than the search space (`s2`), it is physically impossible to find a contiguous block of length `len(s1)` inside `s2`.

**Complexity & Edge Cases:**
Time is O(1) for this immediate check, saving an O(N) full scan. Edge case handled efficiently.

**Why others fail:**
Duplicates in s1 (A) or lowercase s2 (C) are perfectly valid inputs. Non-empty strings (D) do not guarantee failure.

23. **B** `O(n)` time, `O(k)` space

**Explanation:**
Using a monotonic deque ensures that every array element is pushed and popped at most once. Tracking the max for a window of size K requires storing at most K indices in the deque at any time.

**Complexity & Edge Cases:**
Time is strictly O(N). Space is O(K) to maintain the deque. Edge case: K=1 means max is the array itself (deque stays size 1).

**Why others fail:**
O(nk) (C) represents brute force. O(n log n) (A) is a heap approach. O(k) time (D) cannot process the whole array.

24. **D** `k = n`

**Explanation:**
If `k = n`, the window exactly covers the entire array. The loop logic must ensure it doesn't crash on array bounds, and it correctly captures the state of this single full window without attempting to slide further.

**Complexity & Edge Cases:**
Time is O(N). Space depends on state. Failing to handle `k=n` often leads to off-by-one errors where the answer is never recorded.

**Why others fail:**
Cycles (B) are for graphs. Class inheritance (A) and failovers (C) are system design/OOP concepts.

25. **B** check if monotonicity still holds; often switch to prefix sums or deque techniques

**Explanation:**
Sliding window relies on monotonicity (sum strictly increases). Negatives break this, meaning shrinking the left side might *increase* the sum, preventing us from safely finding optimal subarrays. We must pivot to prefix sums + hash maps or deques.

**Complexity & Edge Cases:**
Time complexity changes to O(N) using different data structures. Space becomes O(N). Edge cases include large negative swings.

**Why others fail:**
Using the standard template (A) yields wrong answers. Sorting (C) destroys contiguous subarrays. Ignoring negatives (D) solves the wrong problem.

26. **A** proportional to active distinct symbols or required target symbols

**Explanation:**
For infinite or massive alphabets (like arbitrary Unicode or generic Objects), the hash map size scales with the number of unique elements currently inside the window, capped by K or N.

**Complexity & Edge Cases:**
Space complexity is exactly O(min(N, Alphabet)). Mentioning this distinction demonstrates deep understanding of space bounds.

**Why others fail:**
Always O(1) (D) is false for unbounded alphabets. Impossible (C) is defeatist. Equal to number of windows (B) implies storing every window array.

## Section 4: System Design Adjacency (6 questions)

27. **D** timestamps of recent requests inside the active window

**Explanation:**
A sliding log rate limiter keeps an exact array/list of timestamps for every request. To count valid requests, it prunes timestamps older than `now - window_size`, acting exactly like the left pointer in a variable window.

**Complexity & Edge Cases:**
Time is amortized O(1) per request if pruning is efficient. Space is O(Max Requests in Window), which can be massive under load.

**Why others fail:**
Every request forever (A) causes infinite memory leaks. Sorted names (C) and graph edges (B) do not track time.

28. **D** buckets trade exactness for lower memory and simpler cleanup

**Explanation:**
Storing exact timestamps (sliding log) uses huge memory. Sliding windows in production chunk time into discrete buckets (e.g., 60 one-second counters) to maintain a fixed, predictable memory footprint while sacrificing sub-second precision.

**Complexity & Edge Cases:**
Time per request becomes strict O(1). Space becomes strict O(Buckets). This avoids OutOfMemory errors during DDoS attacks.

**Why others fail:**
Exact logs are more expensive (B). Buckets do not stop time (A) or remove clocks (C).

29. **A** late-arriving events

**Explanation:**
In streaming systems (like Flink/Kafka), data arrives out of order. A strict sliding window based only on processing time will incorrectly drop or assign "late" events to the wrong window. Watermarks and event-time buffers are required.

**Complexity & Edge Cases:**
Space complexity increases because windows must be kept in memory longer to await late arrivals. Edge case: data arriving hours late.

**Why others fail:**
Constructors (B), CSS (C), and Tree rotations (D) are completely unrelated domains.

30. **D** sliding window maximum

**Explanation:**
Calculating a rolling maximum over a live metric stream (like CPU spikes over 5 minutes) is the exact real-world implementation of the sliding window maximum algorithm using a monotonic deque or buckets.

**Complexity & Edge Cases:**
Time is O(1) per metric tick. Space is bounded by the window size or deque size. Edge case: metric stream pauses or drops data.

**Why others fail:**
3-sum (B), N-Queens (C), and LRU cache (A) are algorithmic patterns that do not track contiguous sliding maximums.

31. **A** active window memory per key

**Explanation:**
Sliding window state (hash maps, lists of timestamps) lives in memory. In a distributed rate limiter, monitoring "active window memory per key" is critical because a malicious user spamming requests can cause the state tracking their specific key to bloat and crash the node (OOM).

**Complexity & Edge Cases:**
System stability relies on capping this space complexity, usually by converting sliding logs to fixed-size sliding buckets.

**Why others fail:**
Java classes (B), Line counts (C), and Branch names (D) are codebase metrics, not live production telemetry.

32. **D** "The maintained state is X, validity is Y, each boundary moves at most n times, so time is O(n)."

**Explanation:**
A strong interview wrap-up explicitly ties the code back to the theoretical pattern. By defining the state, the validity invariant, and proving that both pointers move forward at most N times, you rigorously prove O(N) time.

**Complexity & Edge Cases:**
Proving O(N) by citing the 2N pointer movements eliminates ambiguity. Space is explicitly defined based on the state structure.

**Why others fail:**
Passing samples (A) or guessing (B) shows no theoretical depth. Assuming constant space (C) is often wrong (e.g. hash maps). It does not work for all arrays.
