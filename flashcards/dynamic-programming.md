# Dynamic Programming Flashcards

> 40 question-only flashcards for DP state, recurrence, base case, table order, optimization, and system-design transfer mastery.

## Foundations

### Card 1
**Front:** What is the first thing to define in a DP problem?

### Card 2
**Front:** What are overlapping subproblems?

### Card 3
**Front:** What is optimal substructure?

### Card 4
**Front:** What is the difference between top-down memoization and bottom-up tabulation?

### Card 5
**Front:** What does "number of states times transition cost" mean?

### Card 6
**Front:** What makes a DP state key complete?

### Card 7
**Front:** Why are base cases part of correctness, not setup noise?

### Card 8
**Front:** When is greedy preferable to DP?

### Card 9
**Front:** What is an impossible-state sentinel?

### Card 10
**Front:** What should you verify before compressing DP space?

## Core Patterns

### Card 11
**Front:** What does `dp[i]` mean in Climbing Stairs?

### Card 12
**Front:** Why is `dp[0] = 1` useful in counting stair ways?

### Card 13
**Front:** What are the two choices in House Robber?

### Card 14
**Front:** Why does House Robber depend on `i - 1` and `i - 2`?

### Card 15
**Front:** What does `dp[a]` mean in Coin Change minimum coins?

### Card 16
**Front:** Why is Coin Change not generally greedy?

### Card 17
**Front:** What does `dp[i]` mean in Longest Increasing Subsequence?

### Card 18
**Front:** Why does LIS return `max(dp)`?

### Card 19
**Front:** What does `dp[i][j]` mean in Longest Common Subsequence?

### Card 20
**Front:** What are the match and mismatch transitions in LCS?

## Edge Cases and Follow-Ups

### Card 21
**Front:** What does `dp[i]` mean in Word Break?

### Card 22
**Front:** Why is `dp[0] = true` in Word Break?

### Card 23
**Front:** What does `dp[r][c]` mean in Unique Paths?

### Card 24
**Front:** What are first-row and first-column base cases in grid DP?

### Card 25
**Front:** What is the difference between subsequence, substring, and subarray?

### Card 26
**Front:** What can go wrong when using `0` as an impossible value?

### Card 27
**Front:** What is the update-direction risk in compressed knapsack DP?

### Card 28
**Front:** How do you reconstruct a selected path from a DP table?

### Card 29
**Front:** When is sparse memoization better than a full table?

### Card 30
**Front:** What is a good way to explain DP space complexity honestly?

## System Design Transfer

### Card 31
**Front:** How does DP thinking map to staged cost/latency optimization?

### Card 32
**Front:** How does an incomplete DP state resemble an unsafe cache key?

### Card 33
**Front:** What is the production equivalent of an impossible-state sentinel?

### Card 34
**Front:** How does table evaluation order map to pipeline dependency order?

### Card 35
**Front:** How can DP help explain batching or routing trade-offs?

### Card 36
**Front:** What metric should accompany an optimized DP-like production policy?

### Card 37
**Front:** Why is recurrence proof similar to architecture trade-off proof?

### Card 38
**Front:** What does state-space explosion look like in production systems?

### Card 39
**Front:** When should you reject DP in favor of a simpler algorithm?

### Card 40
**Front:** Give a concise interview wrap-up for any DP problem.
