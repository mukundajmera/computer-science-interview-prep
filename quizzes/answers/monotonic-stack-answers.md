# Monotonic Stack Quiz - Answers

### Question 1
**Answer: A) It stores elements in strictly decreasing order from bottom to top.**

**Explanation:**
A monotonic decreasing stack ensures that every new element pushed is smaller than the element below it. When a larger element arrives, we pop the smaller elements, identifying the arriving element as their 'next greater element'.

This explicitly refutes the distractors:
- (It stores elements in strictly increasing order from bottom to top.) is incorrect.
- (It only stores the minimum element seen so far.) is incorrect.
- (It keeps track of the frequency of elements.) is incorrect.

### Question 2
**Answer: A) Encountering a current element that is greater than the element at the top of the stack.**

**Explanation:**
The stack holds elements waiting to find their next greater element. A new, larger element fulfills this requirement for elements at the top of the stack, triggering the pop action.

This explicitly refutes the distractors:
- (Encountering a current element that is smaller than the element at the top of the stack.) is incorrect.
- (When the stack size exceeds a specific limit.) is incorrect.
- (Reaching the end of the array.) is incorrect.

### Question 3
**Answer: A) The indices of histogram bars in strictly increasing order of height.**

**Explanation:**
Storing indices allows us to calculate width accurately. The stack remains strictly increasing by height; when a shorter bar arrives, it forces the resolution of taller bars previously stored, because their rightward extension is now blocked. Storing just heights loses positional data.

This explicitly refutes the distractors:
- (The maximum area calculated so far.) is incorrect.
- (A pair of (height, width) for every element.) is incorrect.
- (The actual heights in strictly decreasing order.) is incorrect.

### Question 4
**Answer: A) width = current_index - stack[-1] - 1 (or current_index if stack is empty).**

**Explanation:**
When popping `top`, the `current_index` acts as the right boundary (the first shorter bar to the right). The new top of the stack `stack[-1]` is the left boundary (the first shorter bar to the left). Thus, the width is exclusively between these boundaries.

This explicitly refutes the distractors:
- (width = current_index - top.) is incorrect.
- (width = stack[-1] - top.) is incorrect.
- (width = current_index + 1.) is incorrect.

### Question 5
**Answer: A) It uses a decreasing stack to find bounding walls; when a taller bar is found, it pops smaller bars to calculate trapped water horizontally.**

**Explanation:**
A decreasing stack maintains potential left boundaries. When a taller right boundary is found, smaller heights in the middle are popped, and the water is calculated horizontally in bounded 'puddles'.

This explicitly refutes the distractors:
- (It uses an increasing stack to find the maximum height on the left and right.) is incorrect.
- (It sorts the array first and processes heights from largest to smallest.) is incorrect.
- (It only keeps track of the absolute maximum height seen so far.) is incorrect.

### Question 6
**Answer: A) A monotonically decreasing double-ended queue (deque).**

**Explanation:**
A deque allows O(1) operations at both ends. We maintain it monotonically decreasing to keep the maximum at the front, while expiring old elements from the front and smaller elements from the back.

This explicitly refutes the distractors:
- (A min-heap priority queue.) is incorrect.
- (A binary search tree.) is incorrect.
- (A standard LIFO stack.) is incorrect.

### Question 7
**Answer: B) All indices of elements that are smaller than or equal to the new element.**

**Explanation:**
Any existing element in the window that is smaller than the newly arriving element will never be the maximum for any future window, so they are safely and permanently discarded from the back.

This explicitly refutes the distractors:
- (The index of the largest element.) is incorrect.
- (The element that just slid out of the window.) is incorrect.
- (All indices of elements greater than the new element.) is incorrect.

### Question 8
**Answer: A) O(N)**

**Explanation:**
Even though there is a while loop inside a for loop, every element is pushed onto the stack exactly once and popped at most once. Thus, there are at most 2N operations, leading to an optimal overall O(N) time complexity.

This explicitly refutes the distractors:
- (O(log N)) is incorrect.
- (O(N^2)) is incorrect.
- (O(N log N)) is incorrect.

### Question 9
**Answer: B) A monotonic decreasing stack storing indices.**

**Explanation:**
'Daily Temperatures' is fundamentally the 'Next Greater Element' problem but asks for the distance (difference in indices) rather than the value itself. Storing indices in a decreasing stack allows trivial distance calculation.

This explicitly refutes the distractors:
- (A min-heap storing temperatures.) is incorrect.
- (A sliding window of fixed size.) is incorrect.
- (A two-pointer approach starting from both ends.) is incorrect.

### Question 10
**Answer: A) Maintain a monotonic decreasing stack of pairs (price, span), accumulating spans when popping smaller prices.**

**Explanation:**
By keeping a decreasing stack of (price, accumulated_span), we can instantly skip over all previously calculated smaller prices in amortized O(1) time per call.

This explicitly refutes the distractors:
- (Linearly scan backwards through all previous prices each day.) is incorrect.
- (Maintain a sorted array of all prices.) is incorrect.
- (Use a Segment Tree to query the maximum in a range.) is incorrect.

### Question 11
**Answer: A) Use an increasing stack to keep digits small, popping larger top elements if we still have 'k' removals left.**

**Explanation:**
To form the smallest number, we want smaller digits at the most significant positions. An increasing stack greedily removes larger preceding digits (peaks) as long as removals (k) are available.

This explicitly refutes the distractors:
- (Remove the smallest digits first.) is incorrect.
- (Use a decreasing stack to keep the largest digits at the bottom.) is incorrect.
- (Sort the digits and pick the first N-K.) is incorrect.

### Question 12
**Answer: A) It finds the distance to the previous and next smaller elements to calculate how many subarrays a specific element is the minimum for.**

**Explanation:**
The total sum is derived by determining the 'span of influence' for each element. By finding the previous and next strictly smaller element using a stack, we determine exactly how many subarrays contain that element as the unique minimum.

This explicitly refutes the distractors:
- (It sorts the subarrays to find the median.) is incorrect.
- (It calculates the sum of all elements directly in a single pass.) is incorrect.
- (It acts as a caching mechanism for range queries.) is incorrect.

### Question 13
**Answer: A) The deque processes elements in amortized O(1) time per element, yielding O(N) overall, whereas a heap takes O(N log K).**

**Explanation:**
The strict time complexity requirement makes the O(N) deque approach optimal. A Max-Heap requires O(log K) for insertions and removals (lazy deletions), resulting in a slower O(N log K) time.

This explicitly refutes the distractors:
- (A deque requires less memory space.) is incorrect.
- (A deque is easier to implement.) is incorrect.
- (A Max-Heap cannot handle duplicate values.) is incorrect.

### Question 14
**Answer: B) It depends on whether strict monotonicity is required by the problem; usually, it is treated the same as a greater element or popped based on edge cases.**

**Explanation:**
If strict monotonicity is required, equals must be popped. If weak monotonicity is allowed, equals are pushed. In problems like 'Sum of Subarray Minimums', one side must be strict and the other weak to avoid double counting. Thus, the action heavily depends on the specific invariant required.

This explicitly refutes the distractors:
- (Throw an error.) is incorrect.
- (Always pop it.) is incorrect.
- (Always ignore the incoming element.) is incorrect.

### Question 15
**Answer: A) A stack where collisions occur if the top is positive and the incoming is negative.**

**Explanation:**
A stack naturally models the LIFO nature of consecutive collisions. We push right-moving asteroids, and when a left-moving asteroid arrives, it iteratively collides with the stack's top.

This explicitly refutes the distractors:
- (A min-heap based on asteroid size.) is incorrect.
- (A sliding window.) is incorrect.
- (A queue where collisions occur at the front.) is incorrect.

### Question 16
**Answer: A) It treats each row as a base and applies the 'Largest Rectangle in Histogram' algorithm on the accumulated heights.**

**Explanation:**
By aggregating vertical counts of consecutive 1s row by row, the problem directly reduces to finding the largest rectangle in a histogram for each row, yielding an optimal O(R * C) time complexity.

This explicitly refutes the distractors:
- (It finds all sub-matrices using four nested loops.) is incorrect.
- (It performs BFS from every '1' in the matrix.) is incorrect.
- (It uses a sweep-line algorithm over the rows.) is incorrect.

### Question 17
**Answer: A) O(N)**

**Explanation:**
In the worst-case scenario (an array strictly increasing in height), every element will be pushed onto the stack before any are popped, resulting in an O(N) auxiliary space requirement.

This explicitly refutes the distractors:
- (O(1)) is incorrect.
- (O(N log N)) is incorrect.
- (O(N^2)) is incorrect.

### Question 18
**Answer: B) Sort by position, then push arrival times to a stack; pop if a car arrives earlier or equal to the car ahead of it.**

**Explanation:**
By iterating backwards (closest to destination first) and checking arrival times, a slower car ahead acts as a bottleneck. If a car arrives faster than the stack's top (the fleet ahead), it joins that fleet (is not pushed). This gracefully tracks independent fleets.

This explicitly refutes the distractors:
- (Maintain a monotonic increasing stack of car positions.) is incorrect.
- (Push speeds to a stack and pop the fastest cars.) is incorrect.
- (Use a stack to reverse the order of cars.) is incorrect.

### Question 19
**Answer: A) Forgetting to process elements remaining in the stack after iterating through the entire array.**

**Explanation:**
Any element left in the stack after the loop finishes means no smaller element was ever found. These must be explicitly handled, usually by assigning them a default value like -1 or the length of the array. Failing to do so leaves dirty data.

This explicitly refutes the distractors:
- (Using a while loop instead of an if statement.) is incorrect.
- (Starting the iteration from the end of the array instead of the beginning.) is incorrect.
- (Storing values instead of frequencies.) is incorrect.

### Question 20
**Answer: B) When the problem requires finding the 'next greater', 'next smaller', 'previous greater', or 'previous smaller' element for items in a sequence.**

**Explanation:**
The defining fingerprint of a monotonic stack is the need to efficiently answer O(N) range queries bounded by inequality ('next greater' or 'previous smaller').

This explicitly refutes the distractors:
- (When the problem involves finding the shortest path in a graph.) is incorrect.
- (When searching for a specific element in a sorted matrix.) is incorrect.
- (When you need to sort an array in O(N log N) time.) is incorrect.
