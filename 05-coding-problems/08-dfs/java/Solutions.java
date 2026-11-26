import java.util.*;

class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    TreeNode() {}
    TreeNode(int val) { this.val = val; }
    TreeNode(int val, TreeNode left, TreeNode right) {
        this.val = val;
        this.left = left;
        this.right = right;
    }
}

public class Solutions {
    // 1. Max Depth
    public int maxDepth(TreeNode root) {
        if (root == null) return 0;
        return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
    }

    // 2. Same Tree
    public boolean isSameTree(TreeNode p, TreeNode q) {
        if (p == null && q == null) return true;
        if (p == null || q == null || p.val != q.val) return false;
        return isSameTree(p.left, q.left) && isSameTree(p.right, q.right);
    }

    // 3. Path Sum
    public boolean hasPathSum(TreeNode root, int targetSum) {
        if (root == null) return false;
        if (root.left == null && root.right == null) return targetSum == root.val;
        return hasPathSum(root.left, targetSum - root.val) || hasPathSum(root.right, targetSum - root.val);
    }

    // 4. Flood Fill
    public int[][] floodFill(int[][] image, int sr, int sc, int color) {
        int startColor = image[sr][sc];
        if (startColor != color) dfsFloodFill(image, sr, sc, startColor, color);
        return image;
    }
    
    private void dfsFloodFill(int[][] image, int r, int c, int startColor, int color) {
        if (r < 0 || r >= image.length || c < 0 || c >= image[0].length || image[r][c] != startColor) return;
        image[r][c] = color;
        dfsFloodFill(image, r+1, c, startColor, color);
        dfsFloodFill(image, r-1, c, startColor, color);
        dfsFloodFill(image, r, c+1, startColor, color);
        dfsFloodFill(image, r, c-1, startColor, color);
    }

    // 5. Number of Islands
    public int numIslands(char[][] grid) {
        if (grid == null || grid.length == 0) return 0;
        int count = 0;
        for (int i = 0; i < grid.length; i++) {
            for (int j = 0; j < grid[0].length; j++) {
                if (grid[i][j] == '1') {
                    count++;
                    dfsIslands(grid, i, j);
                }
            }
        }
        return count;
    }
    
    private void dfsIslands(char[][] grid, int r, int c) {
        if (r < 0 || r >= grid.length || c < 0 || c >= grid[0].length || grid[r][c] != '1') return;
        grid[r][c] = '0';
        dfsIslands(grid, r+1, c);
        dfsIslands(grid, r-1, c);
        dfsIslands(grid, r, c+1);
        dfsIslands(grid, r, c-1);
    }

    // 6. Max Area of Island
    public int maxAreaOfIsland(int[][] grid) {
        int maxArea = 0;
        for (int i = 0; i < grid.length; i++) {
            for (int j = 0; j < grid[0].length; j++) {
                if (grid[i][j] == 1) {
                    maxArea = Math.max(maxArea, dfsArea(grid, i, j));
                }
            }
        }
        return maxArea;
    }
    
    private int dfsArea(int[][] grid, int r, int c) {
        if (r < 0 || r >= grid.length || c < 0 || c >= grid[0].length || grid[r][c] != 1) return 0;
        grid[r][c] = 0;
        return 1 + dfsArea(grid, r+1, c) + dfsArea(grid, r-1, c) + dfsArea(grid, r, c+1) + dfsArea(grid, r, c-1);
    }

    // 7. Find if Path Exists
    public boolean validPath(int n, int[][] edges, int source, int destination) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] edge : edges) {
            adj.get(edge[0]).add(edge[1]);
            adj.get(edge[1]).add(edge[0]);
        }
        boolean[] visited = new boolean[n];
        return dfsValidPath(adj, visited, source, destination);
    }
    
    private boolean dfsValidPath(List<List<Integer>> adj, boolean[] visited, int node, int dest) {
        if (node == dest) return true;
        visited[node] = true;
        for (int neighbor : adj.get(node)) {
            if (!visited[neighbor]) {
                if (dfsValidPath(adj, visited, neighbor, dest)) return true;
            }
        }
        return false;
    }

    // 8. Keys and Rooms
    public boolean canVisitAllRooms(List<List<Integer>> rooms) {
        boolean[] visited = new boolean[rooms.size()];
        dfsRooms(rooms, visited, 0);
        for (boolean v : visited) {
            if (!v) return false;
        }
        return true;
    }
    
    private void dfsRooms(List<List<Integer>> rooms, boolean[] visited, int room) {
        visited[room] = true;
        for (int key : rooms.get(room)) {
            if (!visited[key]) dfsRooms(rooms, visited, key);
        }
    }
}
