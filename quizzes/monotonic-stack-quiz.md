# Monotonic Stack Quiz

**Difficulty:** Advanced | **Time:** 45 minutes

20 coding-pattern questions for Next Greater Element, Largest Rectangle in Histogram, Trapping Rain Water, Sliding Window Maximum deque.

### Question 1
What is the defining characteristic of a monotonic decreasing stack used in the 'Next Greater Element' problem?
- **A)** It stores elements in strictly decreasing order from bottom to top.
- **B)** It stores elements in strictly increasing order from bottom to top.
- **C)** It only stores the minimum element seen so far.
- **D)** It keeps track of the frequency of elements.

### Question 2
In the 'Next Greater Element' problem, what action triggers popping from the stack?
- **A)** Encountering a current element that is greater than the element at the top of the stack.
- **B)** Encountering a current element that is smaller than the element at the top of the stack.
- **C)** When the stack size exceeds a specific limit.
- **D)** Reaching the end of the array.

### Question 3
For the 'Largest Rectangle in Histogram' problem using a monotonic stack, what does the stack store?
- **A)** The indices of histogram bars in strictly increasing order of height.
- **B)** The maximum area calculated so far.
- **C)** A pair of (height, width) for every element.
- **D)** The actual heights in strictly decreasing order.

### Question 4
In 'Largest Rectangle in Histogram', how is the width of the rectangle calculated when popping an element at index 'top' from the stack?
- **A)** width = current_index - stack[-1] - 1 (or current_index if stack is empty).
- **B)** width = current_index - top.
- **C)** width = stack[-1] - top.
- **D)** width = current_index + 1.

### Question 5
How does the monotonic stack approach solve 'Trapping Rain Water'?
- **A)** It uses a decreasing stack to find bounding walls; when a taller bar is found, it pops smaller bars to calculate trapped water horizontally.
- **B)** It uses an increasing stack to find the maximum height on the left and right.
- **C)** It sorts the array first and processes heights from largest to smallest.
- **D)** It only keeps track of the absolute maximum height seen so far.

### Question 6
In 'Sliding Window Maximum', what data structure is used to achieve O(N) time complexity?
- **A)** A monotonically decreasing double-ended queue (deque).
- **B)** A min-heap priority queue.
- **C)** A binary search tree.
- **D)** A standard LIFO stack.

### Question 7
For 'Sliding Window Maximum' using a deque, what is removed from the back of the deque when a new element is added?
- **A)** The index of the largest element.
- **B)** All indices of elements that are smaller than or equal to the new element.
- **C)** The element that just slid out of the window.
- **D)** All indices of elements greater than the new element.

### Question 8
What is the time complexity of solving 'Next Greater Element' using a monotonic stack for an array of size N?
- **A)** O(N)
- **B)** O(log N)
- **C)** O(N^2)
- **D)** O(N log N)

### Question 9
In the 'Daily Temperatures' problem (find how many days until a warmer temperature), what pattern is most suitable?
- **A)** A min-heap storing temperatures.
- **B)** A monotonic decreasing stack storing indices.
- **C)** A sliding window of fixed size.
- **D)** A two-pointer approach starting from both ends.

### Question 10
For the 'Online Stock Span' problem, what is the most efficient way to compute the span of today's price?
- **A)** Maintain a monotonic decreasing stack of pairs (price, span), accumulating spans when popping smaller prices.
- **B)** Linearly scan backwards through all previous prices each day.
- **C)** Maintain a sorted array of all prices.
- **D)** Use a Segment Tree to query the maximum in a range.

### Question 11
How can a monotonic stack be used to solve 'Remove K Digits' to form the smallest possible integer?
- **A)** Use an increasing stack to keep digits small, popping larger top elements if we still have 'k' removals left.
- **B)** Remove the smallest digits first.
- **C)** Use a decreasing stack to keep the largest digits at the bottom.
- **D)** Sort the digits and pick the first N-K.

### Question 12
In 'Sum of Subarray Minimums', how does a monotonic stack help?
- **A)** It finds the distance to the previous and next smaller elements to calculate how many subarrays a specific element is the minimum for.
- **B)** It sorts the subarrays to find the median.
- **C)** It calculates the sum of all elements directly in a single pass.
- **D)** It acts as a caching mechanism for range queries.

### Question 13
Why is a Monotonic Deque preferred over a Max-Heap for the Sliding Window Maximum problem?
- **A)** The deque processes elements in amortized O(1) time per element, yielding O(N) overall, whereas a heap takes O(N log K).
- **B)** A deque requires less memory space.
- **C)** A deque is easier to implement.
- **D)** A Max-Heap cannot handle duplicate values.

### Question 14
For a monotonic increasing stack, if the incoming element is equal to the top of the stack, what is the standard action?
- **A)** Throw an error.
- **B)** It depends on whether strict monotonicity is required by the problem; usually, it is treated the same as a greater element or popped based on edge cases.
- **C)** Always pop it.
- **D)** Always ignore the incoming element.

### Question 15
In the 'Asteroid Collision' problem, when moving right (positive) and left (negative) asteroids meet, what data structure simulates the collisions effectively?
- **A)** A stack where collisions occur if the top is positive and the incoming is negative.
- **B)** A min-heap based on asteroid size.
- **C)** A sliding window.
- **D)** A queue where collisions occur at the front.

### Question 16
How does the monotonic stack approach for 'Maximal Rectangle' in a 2D binary matrix work?
- **A)** It treats each row as a base and applies the 'Largest Rectangle in Histogram' algorithm on the accumulated heights.
- **B)** It finds all sub-matrices using four nested loops.
- **C)** It performs BFS from every '1' in the matrix.
- **D)** It uses a sweep-line algorithm over the rows.

### Question 17
What is the space complexity of solving 'Largest Rectangle in Histogram' using a monotonic stack?
- **A)** O(N)
- **B)** O(1)
- **C)** O(N log N)
- **D)** O(N^2)

### Question 18
In 'Car Fleet', cars moving towards a destination can form fleets. How is a stack used here?
- **A)** Maintain a monotonic increasing stack of car positions.
- **B)** Sort by position, then push arrival times to a stack; pop if a car arrives earlier or equal to the car ahead of it.
- **C)** Push speeds to a stack and pop the fastest cars.
- **D)** Use a stack to reverse the order of cars.

### Question 19
What common pitfall occurs when implementing a monotonic stack to find the Next Smaller Element?
- **A)** Forgetting to process elements remaining in the stack after iterating through the entire array.
- **B)** Using a while loop instead of an if statement.
- **C)** Starting the iteration from the end of the array instead of the beginning.
- **D)** Storing values instead of frequencies.

### Question 20
When should you generally consider using a monotonic stack?
- **A)** When the problem involves finding the shortest path in a graph.
- **B)** When the problem requires finding the 'next greater', 'next smaller', 'previous greater', or 'previous smaller' element for items in a sequence.
- **C)** When searching for a specific element in a sorted matrix.
- **D)** When you need to sort an array in O(N log N) time.
