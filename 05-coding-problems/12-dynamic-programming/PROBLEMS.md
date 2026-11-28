# Dynamic Programming Problems

## 1. Climbing Stairs

**Summary:** Count the distinct ways to climb a staircase when each move covers one or two steps.
**Practice:** [lc-0070-climbing-stairs](../problem-bank/lc-0070-climbing-stairs/README.md)

**Hints:**
1. Think about the last step. To reach step $n$, you must have come from either step $n-1$ or step $n-2$.
2. The total ways to reach step $n$ is the sum of ways to reach step $n-1$ and step $n-2$.
3. This is exactly the Fibonacci sequence. Can you optimize the space?

**Complexity:**
- Time: $O(N)$
- Space: $O(1)$

---

## 2. House Robber

**Summary:** Houses in a row hold money and you cannot take from two adjacent ones; maximise the total.
**Practice:** [lc-0198-house-robber](../problem-bank/lc-0198-house-robber/README.md)

**Hints:**
1. At each house $i$, you have two choices: rob it (which means you can't rob house $i-1$) or skip it.
2. The state transition is $dp[i] = \max(dp[i-1], dp[i-2] + nums[i])$.
3. You only need the last two states to compute the current one, so space can be optimized to $O(1)$.

**Complexity:**
- Time: $O(N)$
- Space: $O(1)$

---

## 3. Word Break

**Summary:** Decide whether a string can be split into a sequence of words from a dictionary.
**Practice:** [lc-0139-word-break](../problem-bank/lc-0139-word-break/README.md)

**Hints:**
1. Use a boolean array `dp` where `dp[i]` represents whether the prefix of `s` of length `i` can be segmented.
2. For each length `i`, check if there exists a previous length `j` such that `dp[j]` is true and the substring `s[j:i]` is in the dictionary.
3. Optimize dictionary lookups by using a HashSet.

**Complexity:**
- Time: $O(N^3)$ or $O(N^2)$ depending on substring extraction
- Space: $O(N)$

---

## 4. Coin Change

**Summary:** Find the fewest coins from given denominations that add up to a target amount, or report that it is impossible.
**Practice:** [lc-0322-coin-change](../problem-bank/lc-0322-coin-change/README.md)

**Hints:**
1. This is a classic unbounded knapsack problem.
2. Let $dp[i]$ be the minimum coins to make amount $i$. $dp[i] = \min(dp[i], 1 + dp[i - coin])$ for each coin.
3. Initialize the DP array with a large value like `amount + 1` to represent impossible states.

**Complexity:**
- Time: $O(N 	imes 	ext{amount})$
- Space: $O(	ext{amount})$

---

## 5. Longest Increasing Subsequence

**Summary:** Find the length of the longest strictly increasing subsequence of an array.
**Practice:** [lc-0300-longest-increasing-subsequence](../problem-bank/lc-0300-longest-increasing-subsequence/README.md)

**Hints:**
1. Let $dp[i]$ be the length of the LIS ending at index $i$.
2. For each element $nums[i]$, look at all previous elements $nums[j]$. If $nums[i] > nums[j]$, then $dp[i] = \max(dp[i], dp[j] + 1)$.
3. An $O(N \log N)$ solution exists using Binary Search and a `tails` array, but the $O(N^2)$ DP is the standard starting point.

**Complexity:**
- Time: $O(N^2)$ (DP) or $O(N \log N)$ (Binary Search)
- Space: $O(N)$

---

## 6. Minimum Path Sum

**Summary:** Find the smallest total cost of a path from the top-left to the bottom-right of a grid, moving only right or down.
**Practice:** [lc-0064-minimum-path-sum](../problem-bank/lc-0064-minimum-path-sum/README.md)

**Hints:**
1. Let `dp[i][j]` be the minimum path sum to reach cell $(i, j)$.
2. You can only arrive at $(i, j)$ from $(i-1, j)$ or $(i, j-1)$. So `dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])`.
3. You can optimize space to $O(N)$ by keeping only the previous row or modifying the grid in-place if allowed.

**Complexity:**
- Time: $O(M 	imes N)$
- Space: $O(N)$ or $O(1)$ in-place

---

## 7. Edit Distance

**Summary:** Compute the minimum number of insert, delete, or replace operations to turn one string into another.
**Practice:** [lc-0072-edit-distance](../problem-bank/lc-0072-edit-distance/README.md)

**Hints:**
1. Let `dp[i][j]` be the edit distance between the first $i$ characters of $word1$ and the first $j$ characters of $word2$.
2. If $word1[i-1] == word2[j-1]$, then `dp[i][j] = dp[i-1][j-1]`.
3. Else, `dp[i][j]` = 1 + min(`dp[i-1][j-1]` (replace), `dp[i-1][j]` (delete), `dp[i][j-1]` (insert)).

**Complexity:**
- Time: $O(M 	imes N)$
- Space: $O(M 	imes N)$ or $O(N)$ optimized

---

## 8. Maximal Square

**Summary:** In a binary grid, find the area of the largest square made only of ones.
**Practice:** [lc-0221-maximal-square](../problem-bank/lc-0221-maximal-square/README.md)

**Hints:**
1. Let `dp[i][j]` be the side length of the maximal square whose bottom-right corner is at $(i, j)$.
2. If `matrix[i][j] == '1'`, `dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1`.
3. The area is the maximum side length squared. Space can be optimized to $O(N)$.

**Complexity:**
- Time: $O(M 	imes N)$
- Space: $O(N)$
