# Backtracking Flashcards

> 40 question-only flashcards for recursive state, pruning, restore discipline, duplicate handling, board constraints, and system-design transfer.

## Foundations

### Card 1
**Front:** What makes a problem a good fit for backtracking?

### Card 2
**Front:** What is the core choose-validate-recurse-undo loop?

### Card 3
**Front:** Why is recursion alone not enough to call an algorithm backtracking?

### Card 4
**Front:** What should every backtracking state define?

### Card 5
**Front:** Why must mutable answers be copied before storing them?

### Card 6
**Front:** What does the invariant "partial state is valid" mean?

### Card 7
**Front:** What is pruning in backtracking?

### Card 8
**Front:** When should backtracking give way to dynamic programming?

### Card 9
**Front:** When should BFS be preferred over backtracking?

### Card 10
**Front:** What space cost must a backtracking answer include?

## Core Patterns

### Card 11
**Front:** What is the recursive state for Subsets?

### Card 12
**Front:** Why does Subsets have `2^n` outputs?

### Card 13
**Front:** What is the base case for Subsets?

### Card 14
**Front:** What state does Permutations need to avoid reusing values?

### Card 15
**Front:** Why is permutation complexity `O(n * n!)` when materializing answers?

### Card 16
**Front:** What does `start` mean in Combination Sum?

### Card 17
**Front:** In Combination Sum, why recurse with `i` when reuse is allowed?

### Card 18
**Front:** What prune is safe for positive sorted candidates in Combination Sum?

### Card 19
**Front:** What is the path-local visited invariant in Word Search?

### Card 20
**Front:** Why must Word Search restore visited cells?

## Edge Cases and Follow-Ups

### Card 21
**Front:** What is the base case ordering risk in Word Search?

### Card 22
**Front:** How does a trie help Word Search II?

### Card 23
**Front:** What is the recursive state for Palindrome Partitioning?

### Card 24
**Front:** Why can Palindrome Partitioning skip non-palindrome prefixes?

### Card 25
**Front:** How can palindrome precomputation improve partitioning?

### Card 26
**Front:** What constraints are tracked in N-Queens?

### Card 27
**Front:** What do `row - col` and `row + col` represent in N-Queens?

### Card 28
**Front:** How does Sudoku compute a `3 x 3` box id?

### Card 29
**Front:** What state must Sudoku restore after a failed digit?

### Card 30
**Front:** How do duplicate candidates change backtracking?

## System Design Transfer

### Card 31
**Front:** How does backtracking map to constraint-based resource placement?

### Card 32
**Front:** What production bug resembles forgetting the undo step?

### Card 33
**Front:** What is the production analogue of a pruning rule?

### Card 34
**Front:** Why do production planners need timeouts around exhaustive search?

### Card 35
**Front:** What metrics reveal backtracking search explosion in production?

### Card 36
**Front:** How can branch-and-bound make a planner safer?

### Card 37
**Front:** What should be logged when a candidate plan is rejected?

### Card 38
**Front:** When is a heuristic fallback acceptable for search?

### Card 39
**Front:** How does memoization change a backtracking search?

### Card 40
**Front:** Give a concise interview wrap-up for any backtracking problem.
