# Union-Find Flashcards

> 40 question-only flashcards for DSU recognition, parent/rank invariants, connected components, cycle detection, identity merging, equality constraints, and system-design transfer.

## Foundations

### Card 1
**Front:** What problem shape suggests Union-Find?

### Card 2
**Front:** What does `find(x)` return?

### Card 3
**Front:** What does `union(a, b)` do?

### Card 4
**Front:** What does it mean when two items have the same root?

### Card 5
**Front:** What does path compression optimize?

### Card 6
**Front:** What does union by rank or size optimize?

### Card 7
**Front:** What is the usual amortized complexity of DSU operations?

### Card 8
**Front:** What state is needed for a component counter?

### Card 9
**Front:** When should a component count decrement?

### Card 10
**Front:** What does Union-Find not tell you about a graph?

## Core Patterns

### Card 11
**Front:** What is the invariant for Number of Connected Components?

### Card 12
**Front:** Why do isolated nodes matter in component counting?

### Card 13
**Front:** What two properties define a valid undirected tree?

### Card 14
**Front:** Why does `edges == n - 1` matter for Graph Valid Tree?

### Card 15
**Front:** What identifies a redundant undirected edge?

### Card 16
**Front:** Why should Redundant Connection check roots before unioning?

### Card 17
**Front:** In Accounts Merge, what should be used as DSU keys?

### Card 18
**Front:** Why is merging by account name incorrect?

### Card 19
**Front:** For Number of Provinces, why does matrix scan dominate?

### Card 20
**Front:** For stones, why model rows and columns as DSU nodes?

## Edge Cases and Follow-Ups

### Card 21
**Front:** How do duplicate edges affect component count?

### Card 22
**Front:** What problem does basic DSU have with edge deletion?

### Card 23
**Front:** Why is DSU not a direct fit for directed reachability?

### Card 24
**Front:** How do you map string keys into DSU ids?

### Card 25
**Front:** Why should grouping call `find` after all unions?

### Card 26
**Front:** How do you track component sizes?

### Card 27
**Front:** What is a rollback DSU used for?

### Card 28
**Front:** In equality equations, why process equalities first?

### Card 29
**Front:** What makes `a!=a` impossible?

### Card 30
**Front:** What collision must be avoided in row-column DSU models?

## System Design Transfer

### Card 31
**Front:** How does Union-Find map to identity merge systems?

### Card 32
**Front:** How does Union-Find map to duplicate clustering?

### Card 33
**Front:** What production risk comes from a false merge?

### Card 34
**Front:** What audit evidence should identity merges keep?

### Card 35
**Front:** What metrics validate a merge pipeline?

### Card 36
**Front:** When should a graph database or traversal replace DSU?

### Card 37
**Front:** What does DSU provide in an append-only relationship stream?

### Card 38
**Front:** What rollback strategy matters for bad production merges?

### Card 39
**Front:** How does DSU relate to connected user/device/account clusters?

### Card 40
**Front:** Give a concise interview wrap-up for any Union-Find problem.
