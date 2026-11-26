# Two Pointers Problems

## 1. Container With Most Water

**Summary:** Given bar heights, choose two bars that, with the gap between them, hold the largest area of water.
**Practice:** [lc-0011-container-with-most-water](problem-bank/lc-0011-container-with-most-water/README.md)

**Hints:**
1. Start with the maximum possible width (pointers at both ends).
2. The area is limited by the shorter line.
3. Moving the taller line inward cannot possibly increase the area. Move the shorter one.

**Complexity:**
- Time: $O(N)$
- Space: $O(1)$

---

## 2. Two Sum II - Input Array Is Sorted

**Summary:** In a sorted array, find the two positions whose values add up to a target.
**Practice:** [lc-0167-two-sum-ii-input-array-is-sorted](problem-bank/lc-0167-two-sum-ii-input-array-is-sorted/README.md)

**Hints:**
1. Use the sorted property to your advantage.
2. If the sum of the elements at the two pointers is too large, how can you reduce it?
3. Decrease the right pointer when sum is too large, increase left when too small.

**Complexity:**
- Time: $O(N)$
- Space: $O(1)$

---

## 3. 3Sum

**Summary:** Find every distinct triple of values in an array that adds up to zero, with no repeated triples.
**Practice:** [lc-0015-3sum](problem-bank/lc-0015-3sum/README.md)

**Hints:**
1. Sorting the array helps in avoiding duplicates and allows the use of two pointers.
2. Fix one element, and then use two pointers for the remaining array to find a sum of `-nums[i]`.
3. Be careful to skip duplicate values for the fixed element and the pointers to avoid duplicate triplets.

**Complexity:**
- Time: $O(N^2)$
- Space: $O(1)$ (or $O(N)$ for sorting)

---

## 4. Valid Triangle Number

**Summary:** Count the triples in an array that could be the side lengths of a triangle.

**Hints:**
1. A valid triangle has sides $a, b, c$ such that $a + b > c$. If sorted $a \le b \le c$, we only need to check $a + b > c$.
2. Sort the array first.
3. Fix the largest side $c$ starting from the end. Use two pointers for $a$ and $b$. If $a+b > c$, all elements between $a$ and $b$ can form a triangle with $b$ and $c$.

**Complexity:**
- Time: $O(N^2)$
- Space: $O(1)$ (or $O(N)$ for sorting)

---

## 5. Move Zeroes

**Summary:** Shift all zeros to the end of an array in place while keeping the order of the other values.
**Practice:** [lc-0283-move-zeroes](problem-bank/lc-0283-move-zeroes/README.md)

**Hints:**
1. Keep a pointer for the position of the next non-zero element.
2. Iterate through the array. When you encounter a non-zero element, swap it with the element at the next non-zero position.
3. Increment the non-zero position pointer only when a swap occurs.

**Complexity:**
- Time: $O(N)$
- Space: $O(1)$

---

## 6. Sort Colors

**Summary:** Sort an array containing only three distinct values in place in a single pass.
**Practice:** [lc-0075-sort-colors](problem-bank/lc-0075-sort-colors/README.md)

**Hints:**
1. This is the Dutch National Flag problem.
2. Use three pointers: one for the boundary of `0`s, one for the boundary of `2`s, and a current pointer to traverse the array.
3. When you see a `0`, swap it with the `0`s boundary and advance both. When you see a `2`, swap with the `2`s boundary and shrink it.

**Complexity:**
- Time: $O(N)$
- Space: $O(1)$

---

## 7. Trapping Rain Water

**Summary:** Given bar heights, compute how much rain would be trapped between the bars.
**Practice:** [lc-0042-trapping-rain-water](problem-bank/lc-0042-trapping-rain-water/README.md)

**Hints:**
1. The water trapped above a bar is determined by the minimum of the maximum heights to its left and right, minus its own height.
2. Instead of finding maxes in separate passes, use two pointers from both ends.
3. Keep track of left max and right max. The smaller of the two maxes bounds the current pointer's water capacity.

**Complexity:**
- Time: $O(N)$
- Space: $O(1)$
