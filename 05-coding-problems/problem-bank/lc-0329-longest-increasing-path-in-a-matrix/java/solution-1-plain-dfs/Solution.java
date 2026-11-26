class Solution {
    private static final int[][] DIRS = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    public int longestIncreasingPath(int[][] matrix) {
        int best = 0;
        for (int row = 0; row < matrix.length; row++) {
            for (int col = 0; col < matrix[0].length; col++) {
                best = Math.max(best, dfs(matrix, row, col));
            }
        }
        return best;
    }

    private int dfs(int[][] matrix, int row, int col) {
        int best = 1;
        for (int[] dir : DIRS) {
            int nextRow = row + dir[0];
            int nextCol = col + dir[1];
            if (nextRow >= 0 && nextCol >= 0 && nextRow < matrix.length && nextCol < matrix[0].length && matrix[nextRow][nextCol] > matrix[row][col]) {
                best = Math.max(best, 1 + dfs(matrix, nextRow, nextCol));
            }
        }
        return best;
    }
}
