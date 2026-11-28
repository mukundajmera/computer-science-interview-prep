# Sliding Window Problems

## 1. Maximum Sum Subarray of Size K

**Summary:** Find the largest sum among all contiguous windows of exactly k elements.

**Hints**:
1. Compute the sum of the first `k` elements.
2. Slide the window: subtract the element leaving the window, add the element entering.
3. Update the maximum sum at each step.

**Complexity**: Time `O(n)`, Space `O(1)`

## 2. Minimum Size Subarray Sum

**Summary:** Find the shortest contiguous run of positive numbers whose sum reaches a target.
**Practice:** [lc-0209-minimum-size-subarray-sum](../problem-bank/lc-0209-minimum-size-subarray-sum/README.md)

**Hints**:
1. Use a variable-size window with `left` and `right` pointers.
2. Expand `right` until the window sum is >= target.
3. Shrink `left` while the sum remains >= target, recording the minimum length.

**Complexity**: Time `O(n)`, Space `O(1)`

## 3. Longest Substring Without Repeating Characters

**Summary:** Find the length of the longest substring in which no character repeats.
**Practice:** [lc-0003-longest-substring-without-repeating-characters](../problem-bank/lc-0003-longest-substring-without-repeating-characters/README.md)

**Hints**:
1. Maintain a frequency map or boolean array for the current window.
2. If a duplicate is found when expanding `right`, advance `left` until the duplicate is removed.
3. Record the maximum window length when valid.

**Complexity**: Time `O(n)`, Space `O(alphabet)`

## 4. Longest Substring With At Most K Distinct Characters

**Summary:** Find the longest substring containing no more than k different characters.

**Hints**:
1. Use a frequency map to track character counts in the window.
2. When the map size exceeds `k`, shrink from the `left` and remove characters with zero count.
3. Record the best length when the map size is <= `k`.

**Complexity**: Time `O(n)`, Space `O(min(k, alphabet))`

## 5. Subarrays With Exactly K Distinct Values

**Summary:** Count the contiguous runs that contain exactly k different values.

**Hints**:
1. Exact K is hard to count directly. Instead, compute `atMost(K) - atMost(K - 1)`.
2. For `atMost(K)`, expand `right` and shrink `left` while distinct values > `K`.
3. The number of valid subarrays ending at `right` is `right - left + 1`.

**Complexity**: Time `O(n)`, Space `O(K)`

## 6. Permutation in String

**Summary:** Decide whether any substring of one string is a rearrangement of another string.

**Hints**:
1. Use a fixed-size window of length `s1.length()`.
2. Compare the frequency map of the window in `s2` with the frequency map of `s1`.
3. Update the frequency map efficiently as the window slides.

**Complexity**: Time `O(len(s1) + len(s2))`, Space `O(alphabet)`

## 7. Sliding Window Maximum

**Summary:** For every window of size k moving across an array, report the largest value.
**Practice:** [lc-0239-sliding-window-maximum](../problem-bank/lc-0239-sliding-window-maximum/README.md)

**Hints**:
1. Maintain a monotonic decreasing deque of indices.
2. Remove indices from the front if they are outside the current window.
3. Remove indices from the back if their values are smaller than the new element.

**Complexity**: Time `O(n)`, Space `O(k)`

