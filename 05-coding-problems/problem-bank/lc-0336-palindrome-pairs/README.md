# Palindrome Pairs

- Canonical ID: `lc-0336-palindrome-pairs`
- Difficulty: `hard`
- Status: `verified`

## Clean-Room Problem Summary

Return every ordered pair of distinct word indices whose concatenation forms a palindrome.

## Driver Signature

- Java: `List<List<Integer>> palindromePairs(String[] words)`
- Python: `palindromePairs(words: List[str]) -> List[List[int]]`

## Key Cases and Invariants

- The pair order matters because word A + word B can differ from word B + word A.
- An empty string pairs with every non-empty palindrome word in both directions.
- Splitting each word lets one side be a palindrome while the other side is matched by a reversed word.

## Solution Ladder

### Tier 1: Brute force pairs

Test every ordered pair by concatenating and checking whether the result is a palindrome.

- Time: `O(n^2 L)` - There are n(n-1) pairs and each check scans up to 2L characters.
- Space: `O(L)` - Only the temporary concatenation/check state is extra beyond output.

### Tier 2: Reversed word map

Index every word, then split each word and match reversed complements when the opposite side is already a palindrome.

- Time: `O(nL^2)` - Each word has L split points and palindrome/reverse work can scan O(L).
- Space: `O(nL)` - The lookup map stores all words.
