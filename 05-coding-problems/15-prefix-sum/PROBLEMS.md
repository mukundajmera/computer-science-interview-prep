# Problems

## 1. Range Sum Query - Immutable

**Summary:** Preprocess a fixed array so the sum of any index range can be answered quickly.

**Hints**:
- Hint 1: What if we precompute the sum from index 0 to `i` for all `i`?
- Hint 2: If we have prefix sums `P[i]`, how can we get the sum of `nums[left...right]`?
- Hint 3: It is simply `P[right + 1] - P[left]` if `P` is 1-indexed.
**Complexity**: O(1) query, O(N) precomputation, O(N) space.

## 2. Subarray Sum Equals K

**Summary:** Count the contiguous runs of an array whose sum equals a target.
**Practice:** [lc-0560-subarray-sum-equals-k](../problem-bank/lc-0560-subarray-sum-equals-k/README.md)

**Hints**:
- Hint 1: We can use a hash map to store the frequency of all prefix sums.
- Hint 2: As we iterate, we compute the current prefix sum `P`. If `P - k` exists in our map, we add its frequency to our result.
- Hint 3: Don't forget to initialize the hash map with `{0: 1}` to handle cases where a prefix sum exactly equals `k`.
**Complexity**: O(N) time, O(N) space.

## 3. Continuous Subarray Sum

**Summary:** Decide whether some contiguous run of at least two numbers adds up to a multiple of k.

**Hints**:
- Hint 1: If `sum % k` repeats, it means the subarray between these two prefix sums is a multiple of `k`.
- Hint 2: Keep track of `prefix_sum % k` in a hash map.
- Hint 3: The map should store the index to ensure the subarray has length >= 2.
**Complexity**: O(N) time, O(N) space.

## 4. Range Sum Query 2D - Immutable

**Summary:** Preprocess a fixed matrix so the sum of any rectangular region can be answered quickly.

**Hints**:
- Hint 1: We can build a 2D prefix sum array where `P[i][j]` is the sum of elements in the rectangle `(0, 0)` to `(i, j)`.
- Hint 2: `P[i][j] = matrix[i-1][j-1] + P[i-1][j] + P[i][j-1] - P[i-1][j-1]`.
- Hint 3: To query, `sum = P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]`.
**Complexity**: O(1) query, O(M*N) precomputation, O(M*N) space.

## 5. Find Pivot Index

**Summary:** Find the position where the sum of everything to its left equals the sum of everything to its right.

**Hints**:
- Hint 1: We can precompute the total sum of the array.
- Hint 2: As we iterate, we can keep track of the left sum.
- Hint 3: The right sum is simply `total_sum - left_sum - nums[i]`. If they are equal, we found the pivot.
**Complexity**: O(N) time, O(1) space.

## 6. Corporate Flight Bookings

**Summary:** Seat reservations are given as ranges of flights with a count; compute the total reserved on each flight.

**Hints**:
- Hint 1: This is a difference array problem. Instead of adding seats to every flight in the range, we can just record the change at the boundaries.
- Hint 2: Add `seats` at index `first - 1` and subtract `seats` at index `last`.
- Hint 3: Then calculate the prefix sum of this difference array to get the final answer.
**Complexity**: O(N + bookings.length) time, O(N) space.
