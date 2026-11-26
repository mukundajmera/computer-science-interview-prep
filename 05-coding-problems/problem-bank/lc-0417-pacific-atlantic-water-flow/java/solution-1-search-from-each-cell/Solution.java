import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    private static final int[][] DIRS = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    public List<List<Integer>> pacificAtlantic(int[][] heights) {
        List<List<Integer>> result = new ArrayList<>();
        for (int row = 0; row < heights.length; row++) {
            for (int col = 0; col < heights[0].length; col++) {
                boolean[] reaches = new boolean[2];
                dfs(row, col, heights[row][col], heights, new boolean[heights.length][heights[0].length], reaches);
                if (reaches[0] && reaches[1]) {
                    result.add(Arrays.asList(row, col));
                }
            }
        }
        return result;
    }

    private void dfs(int row, int col, int previous, int[][] heights, boolean[][] seen, boolean[] reaches) {
        if (row < 0 || col < 0) {
            reaches[0] = true;
            return;
        }
        if (row == heights.length || col == heights[0].length) {
            reaches[1] = true;
            return;
        }
        if (seen[row][col] || heights[row][col] > previous) {
            return;
        }
        seen[row][col] = true;
        for (int[] dir : DIRS) {
            dfs(row + dir[0], col + dir[1], heights[row][col], heights, seen, reaches);
        }
    }
}
