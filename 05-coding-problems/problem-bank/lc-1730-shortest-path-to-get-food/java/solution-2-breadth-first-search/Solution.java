import java.util.ArrayDeque;
import java.util.Queue;

class Solution {
    private static final int[][] DIRS = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    public int getFood(char[][] grid) {
        Queue<int[]> queue = new ArrayDeque<>();
        boolean[][] seen = new boolean[grid.length][grid[0].length];
        for (int row = 0; row < grid.length; row++) {
            for (int col = 0; col < grid[0].length; col++) {
                if (grid[row][col] == '*') {
                    queue.add(new int[] {row, col, 0});
                    seen[row][col] = true;
                }
            }
        }
        while (!queue.isEmpty()) {
            int[] current = queue.remove();
            for (int[] dir : DIRS) {
                int row = current[0] + dir[0];
                int col = current[1] + dir[1];
                if (row < 0 || col < 0 || row == grid.length || col == grid[0].length || seen[row][col] || grid[row][col] == 'X') {
                    continue;
                }
                if (grid[row][col] == '#') {
                    return current[2] + 1;
                }
                seen[row][col] = true;
                queue.add(new int[] {row, col, current[2] + 1});
            }
        }
        return -1;
    }
}
