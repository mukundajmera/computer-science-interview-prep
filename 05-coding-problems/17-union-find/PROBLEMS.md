# Problems

## 1. Number of Provinces

**Summary:** Given a matrix describing which cities are directly linked, count the groups of cities connected directly or indirectly.

**Hints:**
- Think of cities as nodes and connections as edges.
- Each province is a connected component in a graph.
- Union-Find is perfect for counting connected components.

**Complexity:**
- Time: `O(n^2)`
- Space: `O(n)`

## 2. Redundant Connection

**Summary:** A tree had one extra edge added; identify an edge whose removal restores a tree.

**Hints:**
- As you process each edge, use Union-Find.
- If the two nodes of an edge are already in the same set, adding this edge creates a cycle.
- The first such edge found is the redundant one.

**Complexity:**
- Time: `O(n * alpha(n))`
- Space: `O(n)`

## 3. Number of Connected Components in an Undirected Graph

**Summary:** Count how many separate connected groups an undirected graph contains.
**Practice:** [lc-0323-number-of-connected-components-in-an-undirected-graph](../problem-bank/lc-0323-number-of-connected-components-in-an-undirected-graph/README.md)

**Hints:**
- Start with `n` individual components.
- For each edge, union the sets of its endpoints.
- If a union is successful, decrease the component count by 1.

**Complexity:**
- Time: `O(V + E * alpha(V))`
- Space: `O(V)`

## 4. Graph Valid Tree

**Summary:** Decide whether a set of undirected edges over n nodes forms a single tree.
**Practice:** [lc-0261-graph-valid-tree](../problem-bank/lc-0261-graph-valid-tree/README.md)

**Hints:**
- A valid tree with `n` nodes must have exactly `n-1` edges.
- Adding an edge must successfully merge two disconnected components.
- If two nodes are already connected before adding an edge, there's a cycle.

**Complexity:**
- Time: `O(V + E * alpha(V))`
- Space: `O(V)`

## 5. Accounts Merge

**Summary:** Several accounts list email addresses under a name; combine accounts that share any email into one merged record.
**Practice:** [lc-0721-accounts-merge](../problem-bank/lc-0721-accounts-merge/README.md)

**Hints:**
- Connect all emails belonging to the same account.
- Map each unique email to an integer ID to use in Union-Find.
- Group emails by their root ID and sort them before formatting the result.

**Complexity:**
- Time: `O(NK log NK)` where `N` is number of accounts, `K` is max emails per account
- Space: `O(NK)`

## 6. Longest Consecutive Sequence

**Summary:** Find the length of the longest run of consecutive integers present in an unsorted array.
**Practice:** [lc-0128-longest-consecutive-sequence](../problem-bank/lc-0128-longest-consecutive-sequence/README.md)

**Hints:**
- Remove duplicates first.
- For each number `x`, if `x-1` or `x+1` exists, union them.
- The size of the largest connected component is the answer.

**Complexity:**
- Time: `O(n)`
- Space: `O(n)`
