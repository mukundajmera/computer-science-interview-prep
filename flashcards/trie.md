# Trie Flashcards

> 40 question-only flashcards for trie recognition, node contracts, wildcard branching, prefix aggregates, board-search pruning, autocomplete ranking, and system-design transfer.

## Foundations

### Card 1
**Front:** What problem shape suggests a trie?

### Card 2
**Front:** What does each trie node represent?

### Card 3
**Front:** What fields belong in a basic trie node?

### Card 4
**Front:** Why is a terminal marker separate from child existence?

### Card 5
**Front:** What is the difference between exact search and prefix search?

### Card 6
**Front:** What is the time complexity of basic insert/search by word length?

### Card 7
**Front:** What does trie memory depend on?

### Card 8
**Front:** When is a fixed child array better than a child map?

### Card 9
**Front:** When is a child map better than a fixed array?

### Card 10
**Front:** What is a compressed trie?

## Core Patterns

### Card 11
**Front:** What is the invariant for Implement Trie?

### Card 12
**Front:** Why does `startsWith` not require `is_word`?

### Card 13
**Front:** In wildcard search, what does `.` match?

### Card 14
**Front:** Why can wildcard search branch beyond `O(L)`?

### Card 15
**Front:** For Replace Words, why stop at the first terminal node?

### Card 16
**Front:** What state does Map Sum Pairs need besides the trie?

### Card 17
**Front:** What does each Map Sum prefix node store?

### Card 18
**Front:** How does Word Search II combine trie and backtracking?

### Card 19
**Front:** How do you avoid duplicate words in Word Search II?

### Card 20
**Front:** For Longest Word in Dictionary, why only traverse terminal child nodes?

## Edge Cases and Follow-Ups

### Card 21
**Front:** What happens when a word is also a prefix of another word?

### Card 22
**Front:** What should duplicate inserts do?

### Card 23
**Front:** What should Map Sum do when a key is overwritten?

### Card 24
**Front:** What is the risk of substring copying in recursive trie search?

### Card 25
**Front:** What alphabet assumption should be clarified?

### Card 26
**Front:** How would Unicode affect a trie design?

### Card 27
**Front:** How would delete work in a trie?

### Card 28
**Front:** When is a hash set enough instead of a trie?

### Card 29
**Front:** When does a sorted array plus binary search compete with a trie?

### Card 30
**Front:** Why is a trie not a full search engine?

## System Design Transfer

### Card 31
**Front:** How does trie prefix lookup map to autocomplete?

### Card 32
**Front:** What must autocomplete add beyond prefix lookup?

### Card 33
**Front:** Why can precomputing top suggestions at every node be expensive?

### Card 34
**Front:** How would you keep autocomplete suggestions fresh?

### Card 35
**Front:** What metrics validate autocomplete quality?

### Card 36
**Front:** How does trie lookup map to route or command matching?

### Card 37
**Front:** What is the difference between prefix search and full-text relevance?

### Card 38
**Front:** What production abuse risk exists in autocomplete?

### Card 39
**Front:** When would a compressed trie or radix tree matter in production?

### Card 40
**Front:** Give a concise interview wrap-up for any trie problem.
