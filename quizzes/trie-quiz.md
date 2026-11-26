# Trie Quiz

> 32 multiple-choice questions plus written drills to test prefix-index recognition, trie node design, wildcard branching, autocomplete trade-offs, board-search pruning, and system-design transfer.
>
> Time: 40 minutes | Difficulty: Intermediate

## Section 1: Pattern Recognition

### Question 1
What problem shape most strongly suggests a trie?

A) Many prefix queries over a dictionary
B) One pass over a sorted array
C) Finding a shortest path in a weighted graph
D) Computing a numeric median

### Question 2
What must a trie node usually store for basic word search?

A) Only the full dictionary
B) Children and a terminal-word marker
C) A heap and a stack
D) A sorted copy of every input word

### Question 3
What is the difference between `search("app")` and `startsWith("app")` after inserting only `apple`?

A) Both must be false
B) `search` is true and `startsWith` is false
C) `search` is false and `startsWith` is true
D) Both must be true

### Question 4
Which prompt most directly needs wildcard trie DFS?

A) Kth largest element
B) Graph valid tree
C) Minimum window subarray
D) Word Dictionary with `.` matching one character

### Question 5
For Replace Words, why does traversal stop at the first terminal node?

A) It is the shortest dictionary root
B) It is always the longest word
C) It means no replacement exists
D) It sorts the sentence

### Question 6
What extra state is required for Map Sum Pairs updates?

A) A queue of visited nodes only
B) A key-to-current-value map for deltas
C) A matrix of all prefixes
D) A max heap of characters

### Question 7
What does a trie do in Word Search II?

A) Computes shortest paths between cells
B) Sorts board rows
C) Prunes board paths that are not dictionary prefixes
D) Removes the need for visited cells

### Question 8
What does autocomplete need in addition to prefix lookup?

A) Only exact membership
B) Union by rank
C) Matrix diagonal scanning
D) Ranking metadata or a ranker

## Section 2: Invariants and State

### Question 9
What does the path from root to a node represent?

A) A prefix
B) A connected component
C) A sorted heap
D) A graph cycle

### Question 10
When is a trie path an exact stored word?

A) Whenever the path exists
B) When the final node is terminal
C) Only when the node has no children
D) Only when the word is longest

### Question 11
For wildcard search, what happens when the current pattern character is fixed?

A) Try every child
B) Return true immediately
C) Follow only the matching child
D) Delete the node

### Question 12
For wildcard search, what happens when the current pattern character is `.`?

A) Skip any number of characters
B) Match only a period character
C) Restart at the root
D) Try all children for one character position

### Question 13
In Map Sum Pairs, what should each prefix node store?

A) Sum of values for keys in its subtree
B) Only the last inserted key
C) Number of all dictionary words globally
D) A board coordinate

### Question 14
In Word Search II, why store the full word or id at terminal nodes?

A) To compare graph roots
B) To emit found words without rebuilding or duplicating strings awkwardly
C) To sort child maps by frequency
D) To avoid checking visited cells

### Question 15
In Longest Word in Dictionary, which child nodes may DFS enter?

A) Every child node, terminal or not
B) Only leaf nodes
C) Only child nodes that are terminal words
D) Only nodes with two children

### Question 16
What does a compressed trie optimize?

A) Connectivity queries
B) Median retrieval
C) Matrix multiplication
D) Memory and path length for long single-child chains

## Section 3: Complexity and Edge Cases

### Question 17
Basic trie insert/search for word length `L` costs:

A) `O(L)`
B) `O(log n)` regardless of word length
C) `O(n^2)` always
D) `O(1)` with no memory

### Question 18
What is trie memory most directly proportional to?

A) Number of queries only
B) Total stored characters after shared prefixes plus child overhead
C) Board rows squared
D) Heap size `k`

### Question 19
Why is wildcard search not always `O(L)`?

A) Fixed characters cannot be searched
B) Tries cannot handle patterns
C) Wildcards can branch across many children
D) Terminal markers are expensive

### Question 20
What is a common Replace Words bug?

A) Using a terminal marker
B) Preserving unmatched words
C) Building the trie once
D) Returning the longest matching root instead of the shortest

### Question 21
What is a common Map Sum Pairs bug?

A) Adding the new value on overwrite instead of applying the delta
B) Returning zero for missing prefix
C) Storing current values
D) Updating every prefix node

### Question 22
What prevents duplicate output in Word Search II?

A) Reusing the same cell
B) A result set or clearing terminal word after first discovery
C) Sorting the board
D) Removing trie children before search starts

### Question 23
What should be clarified before using a fixed array of 26 children?

A) The graph is undirected
B) Edge count is `n - 1`
C) The input alphabet is lowercase English letters
D) Values are all positive

### Question 24
When might a sorted array plus binary search beat a trie?

A) When wildcard branching is required on every query
B) When board DFS needs prefix pruning
C) When every keystroke needs top suggestions
D) When memory is tighter than latency and prefix queries are modest

## Section 4: System Design Transfer

### Question 25
What production system commonly uses prefix indexing?

A) Autocomplete or command lookup
B) Payment idempotency only
C) CPU scheduling only
D) Password hashing only

### Question 26
What must autocomplete add beyond trie traversal?

A) Only recursion
B) Ranking, freshness, abuse controls, and metrics
C) Only a terminal flag
D) Only graph cycle detection

### Question 27
Why is a trie not enough for full-text search relevance?

A) Prefix lookup is impossible
B) Tries cannot store words
C) Prefix lookup does not provide stemming, ranking, typo tolerance, or phrase relevance
D) Search engines never use indexes

### Question 28
What metric would validate autocomplete quality?

A) Number of parent pointers compressed
B) Count of disconnected components
C) Median heap size
D) Click-through or selection rate for suggestions

### Question 29
What scale risk appears when storing top suggestions at every trie node?

A) Memory growth from duplicated candidate metadata
B) No queries can be answered
C) Every prefix becomes exact-only
D) Ranking becomes unnecessary

### Question 30
What is a strong production answer for hot prefixes?

A) Scan every term on every keystroke forever
B) Cache or precompute capped top suggestions and track freshness
C) Disable ranking
D) Use directed DFS

### Question 31
What should a candidate say about Unicode support?

A) Unicode always fits in 26 children
B) Unicode removes memory costs
C) Child representation and normalization must be explicit
D) Unicode makes terminal flags unnecessary

### Question 32
What is the best concise wrap-up for trie problems?

A) Always sort all words first
B) Always use Union-Find
C) Ignore query semantics
D) Define node metadata, distinguish prefix from word, and state memory trade-offs

## Written Drills

A. Explain why `search("app")` differs from `startsWith("app")`.
B. Walk through wildcard search for pattern `.ad`.
C. Explain the delta update in Map Sum Pairs.
D. Explain how a trie prunes Word Search II.
E. Design autocomplete for read-heavy traffic.
F. Translate trie prefix lookup into a system-design discussion.
