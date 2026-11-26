class Solution {
    public int maximalSquare(char[][] matrix) {
        int rows = matrix.length;
        int cols = matrix[0].length;
        int[][] dp = new int[rows + 1][cols + 1];
        int bestSide = 0;

        for (int row = 1; row <= rows; row++) {
            for (int col = 1; col <= cols; col++) {
                if (matrix[row - 1][col - 1] == '1') {
                    dp[row][col] = 1 + Math.min(
                            dp[row - 1][col - 1],
                            Math.min(dp[row - 1][col], dp[row][col - 1])
                    );
                    bestSide = Math.max(bestSide, dp[row][col]);
                }
            }
        }

        return bestSide * bestSide;
    }
}
