# BFS / DFS Flashcards

> 40 question-only flashcards for traversal, reachability, grid, graph, dependency, and system-design transfer mastery.

## Foundations

### Card 1
**Front:** What is the first modeling step before using BFS or DFS?

### Card 2
**Front:** What problem signal favors BFS over DFS?

### Card 3
**Front:** What problem signal favors DFS over BFS?

### Card 4
**Front:** What does the visited set guarantee?

### Card 5
**Front:** Why should BFS often mark visited at enqueue time?

### Card 6
**Front:** What is the difference between a tree and a general graph for traversal?

### Card 7
**Front:** What is the usual complexity of BFS/DFS on an adjacency-list graph?

### Card 8
**Front:** What auxiliary space must DFS include?

### Card 9
**Front:** What auxiliary space must BFS include?

### Card 10
**Front:** When should a graph traversal loop over every node, not only one start node?

## Problem Patterns

### Card 11
**Front:** What invariant defines binary tree level order traversal?

### Card 12
**Front:** What is the node model in Number of Islands?

### Card 13
**Front:** Why does Number of Islands increment count before flood fill?

### Card 14
**Front:** What map is required for Clone Graph?

### Card 15
**Front:** Why does Clone Graph fail without an original-to-clone map?

### Card 16
**Front:** Why is Rotting Oranges multi-source BFS?

### Card 17
**Front:** What should Rotting Oranges return when fresh cells remain?

### Card 18
**Front:** What do DFS colors mean in Course Schedule?

### Card 19
**Front:** Why is a single boolean visited set insufficient for directed-cycle detection?

### Card 20
**Front:** Why does Word Ladder need BFS?

## Edge Cases and Follow-Ups

### Card 21
**Front:** What is the Word Ladder sequence-length off-by-one risk?

### Card 22
**Front:** How can bidirectional BFS improve Word Ladder?

### Card 23
**Front:** What comparison direction changes in Pacific Atlantic reverse search?

### Card 24
**Front:** Why should grid traversal state whether input mutation is allowed?

### Card 25
**Front:** What changes when graph edges have weights?

### Card 26
**Front:** How do you avoid recursion depth issues in DFS?

### Card 27
**Front:** What makes topological sort different from ordinary traversal?

### Card 28
**Front:** How do disconnected components affect cycle detection?

### Card 29
**Front:** What is frontier explosion?

### Card 30
**Front:** When is reverse reachability better than starting from every source?

## System Design Transfer

### Card 31
**Front:** How does BFS map to a web crawler frontier?

### Card 32
**Front:** How does a visited set map to production deduplication?

### Card 33
**Front:** How does Course Schedule map to workflow orchestration?

### Card 34
**Front:** How does multi-source BFS map to event propagation?

### Card 35
**Front:** What production metric reveals frontier growth risk?

### Card 36
**Front:** What does graph reachability mean in a social-network design?

### Card 37
**Front:** Why can DFS postorder matter in dependency processing?

### Card 38
**Front:** What changes when graph traversal is distributed across shards?

### Card 39
**Front:** What is the production danger of revisiting states?

### Card 40
**Front:** Give a concise interview wrap-up for any BFS/DFS problem.
