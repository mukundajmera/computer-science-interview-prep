class Solution {
    public int[][] generateMatrix(int n) {
        int[][] matrix = new int[n][n];
        int[][] directions = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
        int row = 0;
        int col = 0;
        int direction = 0;
        for (int value = 1; value <= n * n; value++) {
            matrix[row][col] = value;
            int nextRow = row + directions[direction][0];
            int nextCol = col + directions[direction][1];
            if (nextRow < 0 || nextRow >= n || nextCol < 0 || nextCol >= n || matrix[nextRow][nextCol] != 0) {
                direction = (direction + 1) % 4;
                nextRow = row + directions[direction][0];
                nextCol = col + directions[direction][1];
            }
            row = nextRow;
            col = nextCol;
        }
        return matrix;
    }
}
