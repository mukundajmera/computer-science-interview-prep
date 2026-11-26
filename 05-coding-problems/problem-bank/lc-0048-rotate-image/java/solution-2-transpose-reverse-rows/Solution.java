class Solution {
    public void rotate(int[][] matrix) {
        int n = matrix.length;
        for (int row = 0; row < n; row++) {
            for (int col = row + 1; col < n; col++) {
                int tmp = matrix[row][col];
                matrix[row][col] = matrix[col][row];
                matrix[col][row] = tmp;
            }
        }
        for (int row = 0; row < n; row++) {
            int left = 0;
            int right = n - 1;
            while (left < right) {
                int tmp = matrix[row][left];
                matrix[row][left] = matrix[row][right];
                matrix[row][right] = tmp;
                left++;
                right--;
            }
        }
    }
}
