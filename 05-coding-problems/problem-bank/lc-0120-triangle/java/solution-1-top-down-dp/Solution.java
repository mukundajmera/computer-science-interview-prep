import java.util.List;

class Solution {
    public int minimumTotal(List<List<Integer>> triangle) {
        int rows = triangle.size();
        int[][] dp = new int[rows][rows];
        dp[0][0] = triangle.get(0).get(0);

        for (int row = 1; row < rows; row++) {
            List<Integer> values = triangle.get(row);
            for (int col = 0; col <= row; col++) {
                int best = Integer.MAX_VALUE / 4;
                if (col < row) {
                    best = Math.min(best, dp[row - 1][col]);
                }
                if (col > 0) {
                    best = Math.min(best, dp[row - 1][col - 1]);
                }
                dp[row][col] = best + values.get(col);
            }
        }

        int answer = Integer.MAX_VALUE;
        for (int value : dp[rows - 1]) {
            answer = Math.min(answer, value);
        }
        return answer;
    }
}
