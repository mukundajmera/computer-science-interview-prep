# Trie Problems

## 1. Implement Trie (Prefix Tree)

**Summary:** Build a prefix tree supporting word insertion, exact lookup, and prefix lookup.
**Practice:** [lc-0208-implement-trie-prefix-tree](problem-bank/lc-0208-implement-trie-prefix-tree/README.md)

**Hints:**
1. A node needs a map of children and a boolean terminal flag.
2. `search` requires the final node's terminal flag to be true.
3. `startsWith` only requires the path to exist.

**Complexity:**
- Time: `O(L)` per operation, where `L` is word length.
- Space: `O(L)` for insert, `O(1)` for search.

## 2. Word Dictionary (Wildcard Search)

**Summary:** Build a word store that supports adding words and searching with a wildcard that matches any single letter.

**Hints:**
1. Use DFS for searching.
2. If char is fixed, traverse to the child.
3. If char is `.`, branch to all existing children.

**Complexity:**
- Time: `O(L)` for add, `O(M)` for search where `M` is nodes at depth `L` (worst case exponential branching).
- Space: `O(L)` for recursion.

## 3. Replace Words

**Summary:** Given a dictionary of root words, replace each word in a sentence with its shortest matching root.

**Hints:**
1. Build a trie of roots.
2. Traverse the sentence word by word.
3. Stop at the first terminal node to find the shortest root.

**Complexity:**
- Time: `O(N + M)` where `N` is roots total chars, `M` is sentence length.
- Space: `O(N)` for trie.

## 4. Map Sum Pairs

**Summary:** Maintain key-value pairs and answer the sum of values for all keys that start with a prefix.

**Hints:**
1. Keep a separate map to track the current value of each key.
2. Update the trie with `delta = new_val - old_val`.
3. Store the running sum at every node.

**Complexity:**
- Time: `O(L)` for insert and sum.
- Space: `O(Total chars)` for trie and map.

## 5. Word Search II

**Summary:** Find all dictionary words that can be traced through adjacent cells of a letter grid.
**Practice:** [lc-0212-word-search-ii](problem-bank/lc-0212-word-search-ii/README.md)

**Hints:**
1. Build a trie of the words.
2. Run DFS from each cell.
3. Prune paths that don't match any prefix in the trie.

**Complexity:**
- Time: `O(M*N * 4^L)` worst case, but pruned early.
- Space: `O(Total chars)` for trie.

## 6. Design Search Autocomplete System

**Summary:** Build a system that suggests the most popular past sentences for each typed prefix as the user enters characters.

**Hints:**
1. Use a trie. Maintain the current node as the user types.
2. Store the counts of all sentences.
3. Store the top 3 suggestions directly at each trie node for fast retrieval.

**Complexity:**
- Time: `O(L)` per `input` char to update or `O(1)` to lookup.
- Space: `O(Total chars)` with bounded metadata.
