# DFS Problems

## 1. Maximum Depth of Binary Tree

**Summary:** Return the number of nodes along the longest root-to-leaf path of a binary tree.
**Practice:** [lc-0104-maximum-depth-of-binary-tree](../problem-bank/lc-0104-maximum-depth-of-binary-tree/README.md)

**Hints:** 1. Base case is null node. 2. Recursively find max depth of left and right. 3. Add 1 for the current node.
**Complexity:** Time: O(N), Space: O(H)

## 2. Same Tree

**Summary:** Decide whether two binary trees have identical structure and values.
**Practice:** [lc-0100-same-tree](../problem-bank/lc-0100-same-tree/README.md)

**Hints:** 1. Check if both are null. 2. Check if one is null. 3. Compare values and recurse.
**Complexity:** Time: O(N), Space: O(H)

## 3. Path Sum

**Summary:** Decide whether some root-to-leaf path in a binary tree adds up to a target.
**Practice:** [lc-0064-minimum-path-sum](../problem-bank/lc-0064-minimum-path-sum/README.md)

**Hints:** 1. Keep track of current sum. 2. Check at leaf nodes. 3. Subtract value from target.
**Complexity:** Time: O(N), Space: O(H)

## 4. Flood Fill

**Summary:** Recolour a connected region of same-coloured pixels in a grid, starting from a chosen pixel.
**Practice:** [lc-0733-flood-fill](../problem-bank/lc-0733-flood-fill/README.md)

**Hints:** 1. DFS from sr, sc. 2. Change original color to new color. 3. Check bounds.
**Complexity:** Time: O(M*N), Space: O(M*N)

## 5. Number of Islands

**Summary:** Count the separate groups of connected land cells in a grid of land and water.
**Practice:** [lc-0200-number-of-islands](../problem-bank/lc-0200-number-of-islands/README.md)

**Hints:** 1. Loop through grid. 2. If '1', increment count and DFS. 3. DFS marks '1' as '0'.
**Complexity:** Time: O(M*N), Space: O(M*N)

## 6. Max Area of Island

**Summary:** In a grid of land and water, find the size of the largest connected piece of land.

**Hints:** 1. DFS returns area. 2. Area = 1 + dfs(up) + dfs(down) + dfs(left) + dfs(right). 3. Keep track of max.
**Complexity:** Time: O(M*N), Space: O(M*N)

## 7. Find if Path Exists in Graph

**Summary:** Decide whether two given vertices of an undirected graph are connected.

**Hints:** 1. Build adjacency list. 2. DFS from source. 3. Keep visited set.
**Complexity:** Time: O(V+E), Space: O(V+E)

## 8. Keys and Rooms

**Summary:** Each room may contain keys to other rooms; decide whether every room can be opened starting from room zero.

**Hints:** 1. Start DFS at room 0. 2. Keep visited set. 3. Return if visited length == n.
**Complexity:** Time: O(V+E), Space: O(V+E)
