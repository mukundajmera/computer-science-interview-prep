class Solution {
    private static final int[][] DIRS = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
    private int best;

    public int getFood(char[][] grid) {
        best = Integer.MAX_VALUE;
        int[] start = findStart(grid);
        dfs(grid, start[0], start[1], 0);
        return best == Integer.MAX_VALUE ? -1 : best;
    }

    private void dfs(char[][] grid, int row, int col, int distance) {
        if (distance >= best || row < 0 || col < 0 || row == grid.length || col == grid[0].length || grid[row][col] == 'X') {
            return;
        }
        if (grid[row][col] == '#') {
            best = distance;
            return;
        }
        char original = grid[row][col];
        grid[row][col] = 'X';
        for (int[] dir : DIRS) {
            dfs(grid, row + dir[0], col + dir[1], distance + 1);
        }
        grid[row][col] = original;
    }

    private int[] findStart(char[][] grid) {
        for (int row = 0; row < grid.length; row++) {
            for (int col = 0; col < grid[0].length; col++) {
                if (grid[row][col] == '*') {
                    return new int[] {row, col};
                }
            }
        }
        return new int[] {0, 0};
    }
}
