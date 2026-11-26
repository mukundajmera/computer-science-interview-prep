import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    private static final int[][] DIRS = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    public List<List<Integer>> pacificAtlantic(int[][] heights) {
        int rows = heights.length;
        int cols = heights[0].length;
        boolean[][] pacific = new boolean[rows][cols];
        boolean[][] atlantic = new boolean[rows][cols];
        for (int row = 0; row < rows; row++) {
            dfs(row, 0, heights, pacific);
            dfs(row, cols - 1, heights, atlantic);
        }
        for (int col = 0; col < cols; col++) {
            dfs(0, col, heights, pacific);
            dfs(rows - 1, col, heights, atlantic);
        }
        List<List<Integer>> result = new ArrayList<>();
        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                if (pacific[row][col] && atlantic[row][col]) {
                    result.add(Arrays.asList(row, col));
                }
            }
        }
        return result;
    }

    private void dfs(int row, int col, int[][] heights, boolean[][] seen) {
        if (seen[row][col]) {
            return;
        }
        seen[row][col] = true;
        for (int[] dir : DIRS) {
            int nextRow = row + dir[0];
            int nextCol = col + dir[1];
            if (nextRow >= 0 && nextCol >= 0 && nextRow < heights.length && nextCol < heights[0].length && heights[nextRow][nextCol] >= heights[row][col]) {
                dfs(nextRow, nextCol, heights, seen);
            }
        }
    }
}
