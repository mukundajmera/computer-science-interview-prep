from __future__ import annotations

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solutions:
    # 1. Max Depth
    def maxDepth(self, root: TreeNode) -> int:
        if not root:
            return 0
        return 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))

    # 2. Same Tree
    def isSameTree(self, p: TreeNode, q: TreeNode) -> bool:
        if not p and not q:
            return True
        if not p or not q or p.val != q.val:
            return False
        return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)

    # 3. Path Sum
    def hasPathSum(self, root: TreeNode, targetSum: int) -> bool:
        if not root:
            return False
        if not root.left and not root.right:
            return targetSum == root.val
        return self.hasPathSum(root.left, targetSum - root.val) or self.hasPathSum(root.right, targetSum - root.val)

    # 4. Flood Fill
    def floodFill(self, image: list[list[int]], sr: int, sc: int, color: int) -> list[list[int]]:
        start_color = image[sr][sc]
        if start_color == color:
            return image
        
        def dfs(r, c):
            if r < 0 or r >= len(image) or c < 0 or c >= len(image[0]) or image[r][c] != start_color:
                return
            image[r][c] = color
            dfs(r+1, c)
            dfs(r-1, c)
            dfs(r, c+1)
            dfs(r, c-1)
            
        dfs(sr, sc)
        return image

    # 5. Number of Islands
    def numIslands(self, grid: list[list[str]]) -> int:
        if not grid:
            return 0
        count = 0
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == '1':
                    count += 1
                    self._dfs_islands(grid, i, j)
        return count
        
    def _dfs_islands(self, grid, r, c):
        if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0]) or grid[r][c] != '1':
            return
        grid[r][c] = '0'
        self._dfs_islands(grid, r+1, c)
        self._dfs_islands(grid, r-1, c)
        self._dfs_islands(grid, r, c+1)
        self._dfs_islands(grid, r, c-1)

    # 6. Max Area of Island
    def maxAreaOfIsland(self, grid: list[list[int]]) -> int:
        max_area = 0
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == 1:
                    max_area = max(max_area, self._dfs_area(grid, i, j))
        return max_area
        
    def _dfs_area(self, grid, r, c):
        if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0]) or grid[r][c] != 1:
            return 0
        grid[r][c] = 0
        return 1 + self._dfs_area(grid, r+1, c) + self._dfs_area(grid, r-1, c) + self._dfs_area(grid, r, c+1) + self._dfs_area(grid, r, c-1)

    # 7. Find if Path Exists
    def validPath(self, n: int, edges: list[list[int]], source: int, destination: int) -> bool:
        adj = {i: [] for i in range(n)}
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
            
        visited = set()
        
        def dfs(node):
            if node == destination:
                return True
            visited.add(node)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
            return False
            
        return dfs(source)

    # 8. Keys and Rooms
    def canVisitAllRooms(self, rooms: list[list[int]]) -> bool:
        visited = set()
        
        def dfs(room):
            visited.add(room)
            for key in rooms[room]:
                if key not in visited:
                    dfs(key)
                    
        dfs(0)
        return len(visited) == len(rooms)
