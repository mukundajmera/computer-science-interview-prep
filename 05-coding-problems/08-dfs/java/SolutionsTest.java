import java.util.*;

public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();
        int passed = 0;
        int failed = 0;

        // 1. Max Depth
        TreeNode root1 = new TreeNode(3, new TreeNode(9), new TreeNode(20, new TreeNode(15), new TreeNode(7)));
        if (sol.maxDepth(root1) == 3) passed++; else failed++;
        if (sol.maxDepth(null) == 0) passed++; else failed++;

        // 2. Same Tree
        TreeNode p = new TreeNode(1, new TreeNode(2), new TreeNode(3));
        TreeNode q = new TreeNode(1, new TreeNode(2), new TreeNode(3));
        if (sol.isSameTree(p, q)) passed++; else failed++;

        // 3. Path Sum
        if (sol.hasPathSum(p, 3)) passed++; else failed++;
        if (!sol.hasPathSum(p, 5)) passed++; else failed++;

        // 4. Flood Fill
        int[][] image = {{1,1,1},{1,1,0},{1,0,1}};
        int[][] res = sol.floodFill(image, 1, 1, 2);
        if (res[0][0] == 2 && res[1][0] == 2) passed++; else failed++;

        // 5. Number of Islands
        char[][] grid = {
            {'1','1','0','0','0'},
            {'1','1','0','0','0'},
            {'0','0','1','0','0'},
            {'0','0','0','1','1'}
        };
        if (sol.numIslands(grid) == 3) passed++; else failed++;

        // 6. Max Area of Island
        int[][] grid2 = {{1,1},{1,0}};
        if (sol.maxAreaOfIsland(grid2) == 3) passed++; else failed++;

        // 7. Find if Path Exists
        int[][] edges = {{0,1},{1,2},{2,0}};
        if (sol.validPath(3, edges, 0, 2)) passed++; else failed++;

        // 8. Keys and Rooms
        List<List<Integer>> rooms = new ArrayList<>();
        rooms.add(Arrays.asList(1));
        rooms.add(Arrays.asList(2));
        rooms.add(Arrays.asList(3));
        rooms.add(new ArrayList<>());
        if (sol.canVisitAllRooms(rooms)) passed++; else failed++;
        
        System.out.println("Passed: " + passed + ", Failed: " + failed);
        if (failed > 0) throw new RuntimeException("Tests failed");
    }
}
