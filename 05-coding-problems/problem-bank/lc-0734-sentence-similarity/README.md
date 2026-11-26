# Sentence Similarity

- Canonical ID: `lc-0734-sentence-similarity`
- Difficulty: `easy`
- Status: `verified`

## Clean-Room Problem Summary

Determine whether two equal-length sentences are similar when each word pair is either identical or appears in a provided symmetric similarity list.

## Driver Signature

- Java: `boolean areSentencesSimilar(String[] sentence1, String[] sentence2, List<List<String>> similarPairs)`
- Python: `areSentencesSimilar(sentence1: List[str], sentence2: List[str], similarPairs: List[List[str]]) -> bool`

## Key Cases and Invariants

- Similarity is pairwise and does not imply transitive closure.
- The two sentences must have the same number of words.
- Pairs are treated as undirected.

## Solution Ladder

### Tier 1: Pair scan

For each sentence position, scan the similarity list for a direct pair match.

- Time: `O(nm)` - n word positions may scan m pairs.
- Space: `O(1)` - No extra data structure is required.

### Tier 2: Undirected pair set

Store both directions of every pair in a set and check each word position in O(1).

- Time: `O(n + m)` - Build the pair set once and scan both sentences once.
- Space: `O(m)` - The set stores two directed keys per pair.
