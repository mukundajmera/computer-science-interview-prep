# Greedy Problems

## 1. Maximum Subarray

**Summary:** Find the contiguous run of numbers with the largest sum.
**Practice:** [lc-0053-maximum-subarray](problem-bank/lc-0053-maximum-subarray/README.md)

**Hints**: 
1. Kadane's algorithm.
2. If the running sum becomes negative, it's better to start a new subarray.
3. Keep track of the maximum sum seen so far.
**Complexity**: Time $O(N)$, Space $O(1)$

## 2. Maximum Sum Circular Subarray

**Summary:** Find the largest contiguous sum in an array that is treated as wrapping around its ends.
**Practice:** [lc-0918-maximum-sum-circular-subarray](problem-bank/lc-0918-maximum-sum-circular-subarray/README.md)

**Hints**: 
1. A circular subarray can wrap around.
2. Max subarray sum = max(normal max subarray sum, total sum - normal min subarray sum).
3. Handle the edge case where all numbers are negative.
**Complexity**: Time $O(N)$, Space $O(1)$

## 3. Jump Game

**Summary:** Each array value is the farthest jump allowed from that spot; decide whether the last index is reachable.
**Practice:** [lc-0055-jump-game](problem-bank/lc-0055-jump-game/README.md)

**Hints**: 
1. Keep track of the maximum reachable index.
2. Iterate through the array; if current index is > max reachable, return false.
3. Update max reachable at each step.
**Complexity**: Time $O(N)$, Space $O(1)$

## 4. Jump Game II

**Summary:** Using the same jump rule, find the fewest jumps needed to reach the last index.
**Practice:** [lc-0045-jump-game-ii](problem-bank/lc-0045-jump-game-ii/README.md)

**Hints**: 
1. Keep track of the current jump boundary and the farthest we can reach.
2. When we hit the boundary, increment jumps and update boundary to farthest.
3. Stop when the boundary >= last index.
**Complexity**: Time $O(N)$, Space $O(1)$

## 5. Gas Station

**Summary:** Stations on a circular route provide fuel and cost fuel to leave; find a start that completes the loop, if any.
**Practice:** [lc-0134-gas-station](problem-bank/lc-0134-gas-station/README.md)

**Hints**: 
1. If total gas < total cost, it's impossible.
2. If starting at A and failing at B, no station between A and B can be a valid start.
3. Start checking from next station after a failure.
**Complexity**: Time $O(N)$, Space $O(1)$

## 6. Candy

**Summary:** Children in a line have ratings; give everyone at least one candy and more than a lower-rated neighbour, using as few candies as possible.
**Practice:** [lc-0135-candy](problem-bank/lc-0135-candy/README.md)

**Hints**: 
1. Initialize candies array with 1s.
2. Make a forward pass comparing with left neighbor.
3. Make a backward pass comparing with right neighbor, taking max.
**Complexity**: Time $O(N)$, Space $O(N)$

## 7. Next Permutation

**Summary:** Rearrange numbers into the next lexicographically larger ordering, or the smallest ordering if none exists.
**Practice:** [lc-0031-next-permutation](problem-bank/lc-0031-next-permutation/README.md)

**Hints**: 
1. Find the first decreasing element from the end (pivot).
2. Find the smallest element larger than pivot to its right.
3. Swap them and reverse the suffix.
**Complexity**: Time $O(N)$, Space $O(1)$
